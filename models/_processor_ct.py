from typing import Dict, List, Optional, Union
import torch
from transformers import Qwen3VLVideoProcessor
from transformers.image_processing_utils import BatchFeature
from transformers.utils import TensorType
from transformers.image_utils import ImageInput, ChannelDimension

class HoloCTVideoProcessor(Qwen3VLVideoProcessor):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)

    def preprocess(self, videos, videos_txt, **kwargs):
        
        video_grid_override = kwargs.pop("video_grid_override", None)


        return self._preprocess(videos_seg=videos, videos_txt=videos_txt, video_grid_override=video_grid_override, **kwargs)

    def _preprocess(
        self,
        videos_seg: Union[torch.Tensor, List[torch.Tensor]],
        videos_txt: Union[torch.Tensor, List[torch.Tensor]],
        return_tensors=None,
        video_grid_override=None,
        **kwargs,
    ):
        assert videos_seg.ndim == 5, f"videos_seg must be (B,C,D,H,W), got {videos_seg.shape}"
        assert videos_txt.ndim == 5, f"videos_txt must be (B,C,D,H,W), got {videos_txt.shape}"

        
        video_grid_thw = []
        B, C, D, H, W = videos_seg.shape

        patch_size = 16
        

        for i in range(B):
            if video_grid_override is not None:
                
                gD, gH, gW = video_grid_override[i].tolist()
            else:
                
                gD, gH, gW = D // (patch_size*2), H // patch_size, W // patch_size
            video_grid_thw.append([gD, gH, gW])

        video_grid_thw = torch.tensor(video_grid_thw, dtype=torch.long)

        data = {
            "pixel_values_videos_seg": videos_seg,
            "pixel_values_videos_txt": videos_txt,
            "video_grid_thw": video_grid_thw,
        }

        return BatchFeature(data=data, tensor_type=return_tensors) 