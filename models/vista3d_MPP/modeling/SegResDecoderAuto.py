import torch
import torch.nn as nn
from monai.networks.blocks.upsample import UpSample
from monai.networks.layers.factories import Conv
from monai.utils import UpsampleMode
from typing import Union, List
from .segresnetds import SegResBlock, aniso_kernel
import monai


class SegResUplayersAuto(nn.Module):

    def __init__(
        self,
        spatial_dims: int = 3,
        init_filters: int = 32,
        blocks_down: tuple = (1, 2, 2, 4), 
        blocks_up: tuple | None = None,  
        out_channels: int = 2,
        act: tuple | str = "relu",
        norm: tuple | str = "batch",
        upsample_mode: UpsampleMode | str = "deconv",
        anisotropic_scales: tuple | None = None, 
        dsdepth: int = 1, 
    ) -> None:
        super().__init__()

        self.spatial_dims = spatial_dims
        self.init_filters = init_filters
        self.blocks_down = blocks_down
        self.blocks_up = blocks_up
        self.out_channels = out_channels
        self.act = act
        self.norm = norm
        self.upsample_mode = upsample_mode
        self.anisotropic_scales = anisotropic_scales
        self.dsdepth = dsdepth

        n_up = len(blocks_down) - 1
        
        if self.blocks_up is None:
            self.blocks_up = (1,) * n_up

        filters = init_filters * 2**n_up
        self.up_layers_auto = nn.ModuleList() 

        
        for i in range(n_up):
            
            filters = filters // 2
            
            kernel_size, _, stride = (
                aniso_kernel(anisotropic_scales[len(self.blocks_up) - i - 1])
                if anisotropic_scales
                else (3, 1, 2) 
            )

            level_auto = nn.ModuleDict()
            
            level_auto["upsample"] = UpSample(
                mode=upsample_mode,
                spatial_dims=spatial_dims,
                in_channels=2 * filters, 
                out_channels=filters,
                kernel_size=kernel_size,
                scale_factor=stride,
                bias=False,
                align_corners=False,
            )
            
            blocks = [
                SegResBlock( 
                    spatial_dims=spatial_dims,
                    in_channels=filters,
                    kernel_size=kernel_size,
                    norm=norm,
                    act=act,
                )
                for _ in range(self.blocks_up[i])
            ]
            level_auto["blocks"] = nn.Sequential(*blocks)
            
            
            if len(self.blocks_up) - i <= dsdepth:  
                level_auto["head"] = Conv[Conv.CONV, spatial_dims](
                    in_channels=filters,
                    out_channels=out_channels,
                    kernel_size=1,
                    bias=True,
                )
            else:
                level_auto["head"] = nn.Identity()

            self.up_layers_auto.append(level_auto)

        
        if n_up == 0:
            level_auto = nn.ModuleDict(
                {
                    "upsample": nn.Identity(),
                    "blocks": nn.Identity(),
                    "head": Conv[Conv.CONV, spatial_dims](
                        in_channels=filters,
                        out_channels=out_channels,
                        kernel_size=1,
                        bias=True,
                    ),
                }
            )
            self.up_layers_auto.append(level_auto)

    def forward(self, x_down: List[torch.Tensor], is_training: bool = False) -> Union[torch.Tensor, List[torch.Tensor]]:
        
        
        x = x_down[0]
        
        x_down_for_skip = x_down[1:]

        
        if len(x_down_for_skip) == 0:
             
             
             pass 

        outputs_auto: List[torch.Tensor] = []
        
        
        i = 0 
        for level in self.up_layers_auto:
            
            if isinstance(level["upsample"], nn.Identity):
                 
                 pass 
            else:
                x = level["upsample"](x)
                
                if i < len(x_down_for_skip): 
                    x = x + x_down_for_skip[i]
                x = level["blocks"](x)

                
                if not isinstance(level["head"], nn.Identity):
                    outputs_auto.append(level["head"](x))
                i = i + 1


        outputs_auto.reverse() 


        if not is_training or len(outputs_auto) == 1:
            return outputs_auto[0]
        else:
            
            return outputs_auto

class Class_Mapping_Classify(nn.Module):
    def __init__(self, feature_size, hidden_size, use_mlp=False):
        super().__init__()
        self.use_mlp = use_mlp
        
        
        self.feature_projection = nn.Linear(hidden_size, feature_size)
        
        if use_mlp:
            self.mlp = nn.Sequential(
                nn.Linear(feature_size, feature_size),
                nn.InstanceNorm1d(1),
                nn.GELU(),
                nn.Linear(feature_size, feature_size),
            )
        
        self.image_post_mapping = nn.Sequential(
            monai.networks.blocks.UnetrBasicBlock(
                spatial_dims=3,
                in_channels=feature_size,
                out_channels=feature_size,
                kernel_size=3,
                stride=1,
                norm_name="instance",
                res_block=True,
            ),
            monai.networks.blocks.UnetrBasicBlock(
                spatial_dims=3,
                in_channels=feature_size,
                out_channels=feature_size,
                kernel_size=3,
                stride=1,
                norm_name="instance",
                res_block=True,
            ),
        )

    def forward(self, src, class_hidden_features):
        b, c, d, h, w = src.shape
        batch_size, n_classes, hidden_embed = class_hidden_features.shape
        
        
        src = self.image_post_mapping(src)  
        
        
        class_features = self.feature_projection(class_hidden_features)  
        
        
        if self.use_mlp:
            
            class_features_reshaped = class_features.view(-1, class_features.size(-1))
            class_features_transformed = self.mlp(class_features_reshaped)
            class_features = class_features_transformed.view(batch_size, n_classes, -1)
        
        
        src_reshaped = src.view(b, c, -1)  


        masks_flat = torch.bmm(class_features, src_reshaped)  


        masks = masks_flat.view(b, n_classes, d, h, w)


        return masks, class_features


