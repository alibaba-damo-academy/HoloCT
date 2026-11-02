from typing import List, Union, Optional
from transformers import Qwen3VLProcessor, BatchFeature
from transformers.image_utils import ImageInput
from transformers.video_utils import VideoInput
from transformers.processing_utils import ImagesKwargs, MultiModalData, ProcessingKwargs, ProcessorMixin, Unpack, VideosKwargs
from transformers.tokenization_utils_base import PreTokenizedInput, TextInput
import numpy as np

class Qwen3VLVideosProcessorKwargs(VideosKwargs, total=False):
    pass

class Qwen3VLImagesKwargs(ImagesKwargs):
    min_pixels: Optional[int]
    max_pixels: Optional[int]
    patch_size: Optional[int]
    temporal_patch_size: Optional[int]
    merge_size: Optional[int]


class HoloCTProcessorKwargs(ProcessingKwargs, total=False):
    images_kwargs: Qwen3VLImagesKwargs
    videos_kwargs: Qwen3VLVideosProcessorKwargs
    _defaults = {
        "text_kwargs": {
            "padding": False,
            "return_token_type_ids": False,
            "return_mm_token_type_ids": False,
        },
        "videos_kwargs": {"return_metadata": False},
    }

class HoloCTProcessor(Qwen3VLProcessor):

    def __init__(self, image_processor=None, tokenizer=None, video_processor=None, chat_template=None, **kwargs):

        super().__init__(image_processor, tokenizer, video_processor, chat_template=chat_template, **kwargs)

        self.global_token = "<global_feature>"
        self.local_token = "<local_feature>"

    def __call__(
            self,
            images: ImageInput = None,
            text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None,
            videos_seg: VideoInput = None,
            videos_txt: VideoInput = None,
            **kwargs: Unpack[HoloCTProcessorKwargs],
        ) -> BatchFeature:
            output_kwargs = self._merge_kwargs(
                HoloCTProcessorKwargs,
                tokenizer_init_kwargs=self.tokenizer.init_kwargs,
                **kwargs,
            )

            if images is not None:
                image_inputs = self.image_processor(images=images, **output_kwargs["images_kwargs"])
                image_grid_thw = image_inputs["image_grid_thw"]
            else:
                image_inputs = {}
                image_grid_thw = None

            videos_inputs = {}
            video_grid_thw = None

            if videos_seg is not None and videos_txt is not None:

                videos_inputs = self.video_processor(videos=videos_seg, videos_txt=videos_txt, **output_kwargs["videos_kwargs"])
                video_grid_thw = videos_inputs["video_grid_thw"]


            if not isinstance(text, list):
                text = [text]
            
            text = text.copy()  

            
            if image_grid_thw is not None:
                merge_length = self.image_processor.merge_size**2
                index = 0
                for i in range(len(text)):
                    while self.image_token in text[i]:
                        num_image_tokens = image_grid_thw[index].prod() // merge_length
                        text[i] = text[i].replace(self.image_token, "<|placeholder|>" * num_image_tokens, 1)
                        index += 1
                    text[i] = text[i].replace("<|placeholder|>", self.image_token)

            
            if video_grid_thw is not None:
                
                SPACING = 1.5           
                TOTAL_STRIDE = 32       
                GLOBAL_SEQ_LEN = 256    

                merge_length = self.video_processor.merge_size**2
                index = 0
                for i in range(len(text)):
                    while self.video_token in text[i]:
                        grid = video_grid_thw[index] 
                        D_feat, H_feat, W_feat = grid.tolist()
                        
                        
                        frame_seqlen = H_feat * W_feat // merge_length


                        global_placeholder = (
                            self.global_token + 
                            self.vision_start_token + 
                            "<|placeholder|>" * GLOBAL_SEQ_LEN + 
                            self.vision_end_token
                        )


                        detailed_placeholder = self.local_token
                        for k in range(D_feat):
                            
                            center_voxel_idx = k * TOTAL_STRIDE + (TOTAL_STRIDE - 1) / 2
                            abs_pos_mm = center_voxel_idx * SPACING
                            
                            detailed_placeholder += (
                                f"<{abs_pos_mm:.2f}mm>" + 
                                self.vision_start_token + 
                                "<|placeholder|>" * frame_seqlen + 
                                self.vision_end_token
                            )


                        video_placeholder = global_placeholder + detailed_placeholder
                        
                        search_str_with_vision = f"{self.vision_start_token}{self.video_token}{self.vision_end_token}"
                        
                        if search_str_with_vision in text[i]:
                            text[i] = text[i].replace(search_str_with_vision, video_placeholder, 1)
                        else:
                            text[i] = text[i].replace(self.video_token, video_placeholder, 1)
                        
                        index += 1
                    
                    text[i] = text[i].replace("<|placeholder|>", self.video_token)


            return_tensors = output_kwargs["text_kwargs"].pop("return_tensors", None)
            return_mm_token_type_ids = output_kwargs["text_kwargs"].pop("return_mm_token_type_ids", None)
            
            text_inputs = self.tokenizer(text, **output_kwargs["text_kwargs"])
            self._check_special_mm_tokens(text, text_inputs, modalities=["image", "video"])

            if return_mm_token_type_ids:
                array_ids = np.array(text_inputs["input_ids"])
                mm_token_type_ids = np.zeros_like(text_inputs["input_ids"])
                mm_token_type_ids[array_ids == self.image_token_id] = 1
                text_inputs["mm_token_type_ids"] = mm_token_type_ids.tolist()

            return BatchFeature(data={**text_inputs, **image_inputs, **videos_inputs}, tensor_type=return_tensors)