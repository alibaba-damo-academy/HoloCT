import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vista3d_MPP.modeling import (
    SegResEncoder,
    SegResUplayersAuto,
    Class_Mapping_Classify,
)
import torch
import torch.nn as nn
from transformers import Qwen3VLForConditionalGeneration, Qwen3VLModel
from transformers.models.qwen3_vl.modeling_qwen3_vl import (
    Qwen3VLModelOutputWithPast,
    Qwen3VLCausalLMOutputWithPast,
)
from typing import Union, List, Optional, Tuple
from dataclasses import dataclass
import torch.utils.checkpoint as ckpt
from types import SimpleNamespace
from Med3DVLM.model.projector.builder import build_mm_projector
from Med3DVLM.model.encoder.builder import build_vision_tower
import torch.nn.functional as F


@dataclass
class HoloCTModelOutputWithPast(Qwen3VLModelOutputWithPast):
    all_encode_feats_lists: Optional[List[List[torch.Tensor]]] = None
    all_decode_feats_lists: Optional[List[List[torch.Tensor]]] = None


@dataclass
class HoloCTCausalLMOutputWithPast(Qwen3VLCausalLMOutputWithPast):
    bce_dice_loss: Optional[torch.FloatTensor] = None
    masks_pred: Optional[torch.FloatTensor] = None
    masks_labels: Optional[torch.FloatTensor] = None
    sample_types: Optional[torch.FloatTensor] = None
    all_decode_feats_lists: Optional[torch.FloatTensor] = None
    all_encode_feats_lists: Optional[List[List[torch.Tensor]]] = None


class MLP(nn.Module):
    def __init__(self, hidden_dim, output_dim):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):

        return self.mlp(x)


class HoloCT(Qwen3VLModel):
    def __init__(
        self,
        config,
        **kwargs,
    ):

        super().__init__(config)
        self.seg_token_idx = kwargs.pop("seg_token_idx", 151665)
        self.seg_start_idx = kwargs.pop("seg_start_idx", 151666)
        self.seg_end_idx = kwargs.pop("seg_end_idx", 151667)

        video_encoder_config = {
            "spatial_dims": 3,
            "init_filters": 48,
            "in_channels": 1,
            "blocks_down": (1, 2, 2, 4, 4),
            "norm": "instance",
        }

        mm_projector_config = {
            "mm_projector_type": "mixer",
            "low_input_size": (256, 384),
            "low_output_size": [192, 128],
            "high_input_size": (32, 768),
            "high_output_size": [64, 128],
            "hidden_size": config.vision_config.out_hidden_size,
            "mm_mlp_depth": 2,
            "proj_out_num": 256,
        }

        vision_tower_config = {
            "vision_tower": "dcformer",
            "input_size": (256, 256, 128),
            "dim": 64,
            "vision_select_layer": 0,
            "vision_select_feature": "cls_patch",
        }

        self.mm_projector = build_mm_projector(SimpleNamespace(**mm_projector_config))

        self.vision_tower = build_vision_tower(SimpleNamespace(**vision_tower_config))

        self.video_encoder = SegResEncoder(**video_encoder_config)

        self.use_video_checkpoint = kwargs.pop("use_video_checkpoint", False)

        self.med3dmlp = MLP(hidden_dim=768, output_dim=config.vision_config.hidden_size)

        self.cache_for_seg_infer = False
        self.cached_encode_feats = None

    def get_rope_index(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        image_grid_thw: Optional[torch.LongTensor] = None,
        video_grid_thw: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:

        if video_grid_thw is not None:
            new_video_grids = []
            GLOBAL_SEQ_LEN = 256

            for grid in video_grid_thw:
                D, H, W = grid[0].item(), grid[1].item(), grid[2].item()

                new_video_grids.append([1, -1, GLOBAL_SEQ_LEN])

                for _ in range(D):
                    new_video_grids.append([1, H, W])

            video_grid_thw = torch.tensor(new_video_grids, device=video_grid_thw.device)

        spatial_merge_size = self.config.vision_config.spatial_merge_size
        image_token_id = self.config.image_token_id
        video_token_id = self.config.video_token_id
        vision_start_token_id = self.config.vision_start_token_id
        mrope_position_deltas = []

        if input_ids is not None and (
            image_grid_thw is not None or video_grid_thw is not None
        ):
            total_input_ids = input_ids
            if attention_mask is None:
                attention_mask = torch.ones_like(total_input_ids)
            position_ids = torch.ones(
                3,
                input_ids.shape[0],
                input_ids.shape[1],
                dtype=input_ids.dtype,
                device=input_ids.device,
            )
            image_index, video_index = 0, 0
            attention_mask = attention_mask.to(total_input_ids.device)

            for i, input_ids in enumerate(total_input_ids):
                input_ids = input_ids[attention_mask[i] == 1]
                image_nums, video_nums = 0, 0
                vision_start_indices = torch.argwhere(
                    input_ids == vision_start_token_id
                ).squeeze(1)
                vision_tokens = input_ids[vision_start_indices + 1]
                image_nums = (vision_tokens == image_token_id).sum()
                video_nums = (vision_tokens == video_token_id).sum()
                input_tokens = input_ids.tolist()
                llm_pos_ids_list: list = []
                st = 0
                remain_images, remain_videos = image_nums, video_nums

                for _ in range(image_nums + video_nums):
                    if image_token_id in input_tokens and remain_images > 0:
                        ed_image = input_tokens.index(image_token_id, st)
                    else:
                        ed_image = len(input_tokens) + 1
                    if video_token_id in input_tokens and remain_videos > 0:
                        ed_video = input_tokens.index(video_token_id, st)
                    else:
                        ed_video = len(input_tokens) + 1

                    if ed_image < ed_video:
                        t, h, w = (
                            image_grid_thw[image_index][0],
                            image_grid_thw[image_index][1],
                            image_grid_thw[image_index][2],
                        )
                        image_index += 1
                        remain_images -= 1
                        ed = ed_image
                    else:
                        t, h, w = (
                            video_grid_thw[video_index][0],
                            video_grid_thw[video_index][1],
                            video_grid_thw[video_index][2],
                        )
                        video_index += 1
                        remain_videos -= 1
                        ed = ed_video

                    llm_grid_t = t.item()
                    is_global_feature = h.item() == -1

                    if is_global_feature:
                        llm_grid_h, llm_grid_w = -1, w.item()
                    else:
                        llm_grid_h = h.item()
                        llm_grid_w = w.item()

                    text_len = ed - st
                    st_idx = (
                        llm_pos_ids_list[-1].max() + 1
                        if len(llm_pos_ids_list) > 0
                        else 0
                    )

                    if text_len > 0:
                        llm_pos_ids_list.append(
                            torch.arange(text_len).view(1, -1).expand(3, -1) + st_idx
                        )

                    if is_global_feature:
                        global_seq_len = llm_grid_w
                        llm_pos_ids_list.append(
                            torch.arange(global_seq_len).view(1, -1).expand(3, -1)
                            + text_len
                            + st_idx
                        )
                        st = ed + global_seq_len
                    else:
                        t_index = (
                            torch.arange(llm_grid_t)
                            .view(-1, 1)
                            .expand(-1, llm_grid_h * llm_grid_w)
                            .flatten()
                        )
                        h_index = (
                            torch.arange(llm_grid_h)
                            .view(1, -1, 1)
                            .expand(llm_grid_t, -1, llm_grid_w)
                            .flatten()
                        )
                        w_index = (
                            torch.arange(llm_grid_w)
                            .view(1, 1, -1)
                            .expand(llm_grid_t, llm_grid_h, -1)
                            .flatten()
                        )
                        llm_pos_ids_list.append(
                            torch.stack([t_index, h_index, w_index]) + text_len + st_idx
                        )
                        st = ed + llm_grid_t * llm_grid_h * llm_grid_w

                if st < len(input_tokens):
                    st_idx = (
                        llm_pos_ids_list[-1].max() + 1
                        if len(llm_pos_ids_list) > 0
                        else 0
                    )
                    text_len = len(input_tokens) - st
                    llm_pos_ids_list.append(
                        torch.arange(text_len).view(1, -1).expand(3, -1) + st_idx
                    )

                llm_positions = torch.cat(llm_pos_ids_list, dim=1).reshape(3, -1)
                position_ids[..., i, attention_mask[i] == 1] = llm_positions.to(
                    position_ids.device
                )
                mrope_position_deltas.append(
                    llm_positions.max() + 1 - len(total_input_ids[i])
                )

            mrope_position_deltas = torch.tensor(
                mrope_position_deltas, device=input_ids.device
            ).unsqueeze(1)
            return position_ids, mrope_position_deltas

        else:
            if attention_mask is not None:
                position_ids = attention_mask.long().cumsum(-1) - 1
                position_ids.masked_fill_(attention_mask == 0, 1)
                position_ids = (
                    position_ids.unsqueeze(0)
                    .expand(3, -1, -1)
                    .to(attention_mask.device)
                )
                max_position_ids = position_ids.max(0, keepdim=False)[0].max(
                    -1, keepdim=True
                )[0]
                mrope_position_deltas = max_position_ids + 1 - attention_mask.shape[-1]
            else:
                position_ids = (
                    torch.arange(input_ids.shape[1], device=input_ids.device)
                    .view(1, 1, -1)
                    .expand(3, input_ids.shape[0], -1)
                )
                mrope_position_deltas = torch.zeros(
                    [input_ids.shape[0], 1],
                    device=input_ids.device,
                    dtype=input_ids.dtype,
                )

            return position_ids, mrope_position_deltas

    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        pixel_values: Optional[torch.Tensor] = None,
        pixel_values_videos_seg: Optional[torch.FloatTensor] = None,
        pixel_values_videos_txt: Optional[torch.FloatTensor] = None,
        image_grid_thw: Optional[torch.LongTensor] = None,
        video_grid_thw: Optional[torch.LongTensor] = None,
        cache_position: Optional[torch.LongTensor] = None,
        video_original_shape: Optional[torch.Tensor] = None,
        return_encode_feats: bool = False,
        **kwargs,
    ) -> Union[Tuple, Qwen3VLModelOutputWithPast]:

        if inputs_embeds is None:
            inputs_embeds = self.get_input_embeddings()(input_ids)

        has_video_token = (
            (input_ids == self.config.video_token_id).any()
            if input_ids is not None
            else False
        )

        image_mask = None
        deepstack_visual_embeds = None

        if pixel_values is not None:
            pixel_values = pixel_values.type(self.visual.dtype)
            image_embeds, deepstack_image_embeds = self.visual(
                pixel_values, grid_thw=image_grid_thw
            )

            image_embeds = torch.cat(image_embeds, dim=0).to(
                inputs_embeds.device, inputs_embeds.dtype
            )

            image_mask, _ = self.get_placeholder_mask(
                input_ids, inputs_embeds=inputs_embeds, image_features=image_embeds
            )
            inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds)

            if pixel_values_videos_seg is None:
                deepstack_visual_embeds = deepstack_image_embeds

        all_encode_feats_lists = []

        if (
            has_video_token
            and pixel_values_videos_seg is not None
            and pixel_values_videos_txt is not None
            and video_original_shape is not None
        ):
            if self.use_video_checkpoint:
                vqa_hidden_states = ckpt.checkpoint(
                    self.vision_tower, pixel_values_videos_txt, use_reentrant=False
                )
            else:
                vqa_hidden_states = self.vision_tower(pixel_values_videos_txt)

            feat_low = vqa_hidden_states[-2]
            feat_high = vqa_hidden_states[-1]

            if feat_high.ndim > 3:
                feat_high = feat_high.flatten(2).transpose(1, 2)

            projector_input = (feat_low, feat_high)

            if self.use_video_checkpoint:
                global_video_embeds = ckpt.checkpoint(
                    self.mm_projector, projector_input, use_reentrant=False
                )
            else:
                global_video_embeds = self.mm_projector(projector_input)

            seg_feats_list = []
            seg_grid_shapes = []

            seg_inputs_list = []
            if video_original_shape is not None:
                for b in range(pixel_values_videos_seg.size(0)):
                    d, h, w = video_original_shape[b].tolist()
                    seg_inputs_list.append(pixel_values_videos_seg[b, :, :d, :h, :w])
            else:
                seg_inputs_list = [t for t in pixel_values_videos_seg]

            for vid in seg_inputs_list:
                vid = vid.unsqueeze(0).type(self.visual.dtype).to(inputs_embeds.device)

                if self.use_video_checkpoint:
                    x_down = ckpt.checkpoint(
                        self.video_encoder, vid, use_reentrant=False
                    )
                else:
                    x_down = self.video_encoder(vid)

                x_down_rev = list(reversed(x_down))

                if return_encode_feats or (
                    self.cache_for_seg_infer and not self.training
                ):
                    all_encode_feats_lists.append(x_down_rev)

                seg_feat_map = x_down[-1]

                seg_feat_pooled = F.avg_pool3d(
                    seg_feat_map, kernel_size=(2, 1, 1), stride=(2, 1, 1)
                )

                _, _, dp, hp, wp = seg_feat_pooled.shape
                seg_grid_shapes.append((dp, hp, wp))

                seg_feat_flat = seg_feat_pooled.flatten(2).transpose(1, 2).squeeze(0)
                seg_feats_list.append(seg_feat_flat)

            local_embeds = None
            if len(seg_feats_list) > 0:
                all_seg_feats = torch.cat(seg_feats_list, dim=0)

                if self.use_video_checkpoint:
                    all_seg_feats = ckpt.checkpoint(
                        self.med3dmlp, all_seg_feats, use_reentrant=False
                    )
                else:
                    all_seg_feats = self.med3dmlp(all_seg_feats)

                merged_feats_list = []
                start_idx = 0
                for dp, hp, wp in seg_grid_shapes:
                    if hp % 2 != 0 or wp % 2 != 0:
                        raise ValueError(f"H and W must be even! Got H={hp}, W={wp}.")

                    num_tokens = dp * hp * wp
                    curr_feat = all_seg_feats[start_idx : start_idx + num_tokens]
                    C_mlp = curr_feat.shape[-1]

                    curr_feat = curr_feat.view(dp, hp, wp, C_mlp)
                    curr_feat = curr_feat.view(dp, hp // 2, 2, wp // 2, 2, C_mlp)
                    curr_feat = curr_feat.permute(0, 1, 3, 2, 4, 5)
                    curr_feat = curr_feat.reshape(dp, hp // 2, wp // 2, 4, C_mlp)

                    merged_feats_list.append(curr_feat.reshape(-1, 4, C_mlp))
                    start_idx += num_tokens

                all_feats_merged_input = torch.cat(merged_feats_list, dim=0)
                local_embeds = self.visual.merger(all_feats_merged_input)

            combined_embeds_list = []
            local_start_idx = 0
            rope_grid_thw_list = []

            for b, (dp, hp, wp) in enumerate(seg_grid_shapes):
                g_emb = global_video_embeds[b]
                combined_embeds_list.append(g_emb)

                h_merged = hp // 2
                w_merged = wp // 2
                merged_tokens = dp * h_merged * w_merged

                if local_embeds is not None:
                    l_emb = local_embeds[
                        local_start_idx : local_start_idx + merged_tokens
                    ]
                    combined_embeds_list.append(l_emb)
                    local_start_idx += merged_tokens

                rope_grid_thw_list.append([dp, h_merged, w_merged])

            final_video_embeds_flat = torch.cat(combined_embeds_list, dim=0)

            mask = input_ids == self.config.video_token_id

            num_video_tokens = int(mask.sum().item())
            num_video_features = int(final_video_embeds_flat.shape[0])

            if num_video_tokens != num_video_features:
                raise ValueError(
                    "Video token/feature count mismatch: "
                    f"video_tokens={num_video_tokens}, "
                    f"video_features={num_video_features}, "
                    f"seg_grid_shapes={seg_grid_shapes}"
                )

            mask_expanded = (
                mask.unsqueeze(-1).expand_as(inputs_embeds).to(inputs_embeds.device)
            )
            inputs_embeds = inputs_embeds.masked_scatter(
                mask_expanded, final_video_embeds_flat.to(inputs_embeds.dtype)
            )

            deepstack_visual_embeds = None

            video_grid_thw_tensor = torch.tensor(
                rope_grid_thw_list, device=inputs_embeds.device
            )

            if self.cache_for_seg_infer and not self.training:
                self.cached_encode_feats = all_encode_feats_lists

        else:
            video_grid_thw_tensor = video_grid_thw
            pass

        if attention_mask is not None:
            attention_mask = attention_mask.to(inputs_embeds.device)

        if position_ids is None:
            attention_mask_tensor = (
                attention_mask
                if not isinstance(attention_mask, dict)
                else attention_mask["full_attention"]
            )
            if attention_mask_tensor is not None and attention_mask_tensor.ndim == 4:
                attention_mask_tensor = torch.diagonal(
                    attention_mask_tensor[:, 0], dim1=1, dim2=2
                )
                if attention_mask_tensor.dtype.is_floating_point:
                    attention_mask_tensor = (
                        attention_mask_tensor
                        / torch.finfo(attention_mask_tensor.dtype).min
                    )
                    attention_mask_tensor = (1.0 - attention_mask_tensor).int()

            if (
                (cache_position is not None and cache_position[0] == 0)
                or self.rope_deltas is None
                or (past_key_values is None or past_key_values.get_seq_length() == 0)
            ):
                position_ids, rope_deltas = self.get_rope_index(
                    input_ids=input_ids,
                    image_grid_thw=image_grid_thw,
                    video_grid_thw=video_grid_thw_tensor,
                    attention_mask=attention_mask_tensor,
                )
                self.rope_deltas = rope_deltas
            else:
                batch_size, seq_length, _ = inputs_embeds.shape
                delta = (
                    (cache_position[0] + self.rope_deltas).to(inputs_embeds.device)
                    if cache_position is not None
                    else 0
                )
                position_ids = torch.arange(seq_length, device=inputs_embeds.device)
                position_ids = position_ids.view(1, -1).expand(batch_size, -1)
                if cache_position is not None:
                    delta = delta.repeat_interleave(batch_size // delta.shape[0], dim=0)
                position_ids = position_ids.add(delta)
                position_ids = position_ids.unsqueeze(0).expand(3, -1, -1)

        visual_pos_masks = None
        if deepstack_visual_embeds is not None:
            if image_mask is not None:
                visual_pos_masks = image_mask[..., 0]

        requested_use_cache = kwargs.get("use_cache", None)

        llm_use_cache = (
            False
            if self.training
            else (True if requested_use_cache is None else requested_use_cache)
        )

        outputs = self.language_model(
            input_ids=None,
            position_ids=position_ids,
            attention_mask=attention_mask,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=llm_use_cache,
            cache_position=cache_position,
            visual_pos_masks=visual_pos_masks,
            deepstack_visual_embeds=deepstack_visual_embeds,
            return_dict=True,
            output_hidden_states=False
            if self.training
            else kwargs.get("output_hidden_states", self.config.output_hidden_states),
        )

        return HoloCTModelOutputWithPast(
            last_hidden_state=outputs.last_hidden_state,
            past_key_values=None if self.training else outputs.past_key_values,
            hidden_states=None if self.training else outputs.hidden_states,
            attentions=None if self.training else outputs.attentions,
            rope_deltas=self.rope_deltas,
            all_encode_feats_lists=all_encode_feats_lists
            if pixel_values_videos_seg is not None
            else None,
        )


class HoloCTForConditionalGeneration(Qwen3VLForConditionalGeneration):
    def __init__(
        self,
        config,
        **kwargs,
    ):

        super().__init__(config)

        del self.model

        self.model = HoloCT(config, **kwargs)

        self.post_init()

        self.seg_token_idx = kwargs.pop("seg_token_idx", 151665)
        self.seg_start_idx = kwargs.pop("seg_start_idx", 151666)
        self.seg_end_idx = kwargs.pop("seg_end_idx", 151667)

        video_uplayers_config = {
            "spatial_dims": 3,
            "init_filters": 48,
            "blocks_down": (1, 2, 2, 4, 4),
            "dsdepth": 1,
            "out_channels": 48,
            "norm": "instance",
        }

        self.video_uplayers = SegResUplayersAuto(**video_uplayers_config)
        self.video_mask_decoder = Class_Mapping_Classify(
            feature_size=48,
            hidden_size=config.vision_config.out_hidden_size,
            use_mlp=True,
        )

        self.use_video_checkpoint = kwargs.pop("use_video_checkpoint", False)

    def decode_features(self, x_down_rev: List[torch.Tensor]) -> List[torch.Tensor]:
        feats = self.video_uplayers(x_down_rev)
        if isinstance(feats, torch.Tensor):
            feat_list = [feats]
        else:
            feat_list = list(feats)

        if len(feat_list) == 0:
            raise RuntimeError(
                "The decoder returned no feature maps; check video_uplayers."
            )

        k = min(self.video_uplayers.dsdepth, len(feat_list))
        feat_list = feat_list[:k]

        return feat_list

    def mask_from_features(
        self, feat_list: List[torch.Tensor], class_hidden_features: torch.Tensor
    ) -> Union[torch.Tensor, List[torch.Tensor]]:
        masks_list = []
        for feat in feat_list:
            class_hidden_features = class_hidden_features.to(dtype=feat.dtype)

            if self.use_video_checkpoint:
                masks, _ = ckpt.checkpoint(
                    self.video_mask_decoder,
                    feat,
                    class_hidden_features,
                    use_reentrant=False,
                )
            else:
                masks, _ = self.video_mask_decoder(feat, class_hidden_features)
            masks_list.append(masks)

        if len(masks_list) == 1:
            return masks_list[0]

        return masks_list

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        pixel_values=None,
        pixel_values_videos_seg: Optional[torch.FloatTensor] = None,
        pixel_values_videos_txt: Optional[torch.FloatTensor] = None,
        video_original_shape=None,
        skip_uplayer=False,
        **kwargs,
    ):
        if (
            self.training
            or kwargs.get("labels") is not None
            or kwargs.get("masks_labels") is not None
        ):
            raise RuntimeError(
                "This release supports inference only. Call model.eval() without training labels."
            )
        return self.forward_generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            pixel_values_videos_seg=pixel_values_videos_seg,
            pixel_values_videos_txt=pixel_values_videos_txt,
            video_original_shape=video_original_shape,
            skip_uplayer=skip_uplayer,
            **kwargs,
        )

    @torch.no_grad()
    def forward_generate(self, input_ids, skip_uplayer, **kwargs):

        outputs = self.model(input_ids=input_ids, skip_uplayer=skip_uplayer, **kwargs)

        hidden_states = outputs.last_hidden_state
        logits = self.lm_head(hidden_states)

        return HoloCTCausalLMOutputWithPast(
            loss=None,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            rope_deltas=outputs.rope_deltas,
            all_encode_feats_lists=outputs.all_encode_feats_lists,
        )
