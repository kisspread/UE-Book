# BaseMaterial

> Unified base material function repository

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | true |
| 包含内容 | true |
| 模块 | 无（纯内容插件） |
| 创建时间 | 2025-08-03 |
| 年龄标签 | 🆕 |
| Beta | ⚠️ IsBetaVersion = true |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/BaseMaterial) | （纯内容，无源码） |

## 用途

BaseMaterial 是 UE5 新推出的**统一材质函数库**插件，提供一套标准化的材质构建模块（Material Functions、Material Layers、Material Layer Blends、Parent Materials），供美术和技术美术在项目中复用，而不需要从零搭建材质图。

这个插件的核心价值在于：

1. **坐标映射系统**：提供多种 UV 映射方案（Triplanar、Biplanar、Octaplanar、CellBombing、HexTile、CircleSplat 等），每种都带有 Basic / Dither / POM 三种变体，解决复杂几何体上的贴图问题
2. **统一采样管线**：通过 `MF_ResolveCoordinateFrame_*` 系列函数将不同映射方式统一到相同的输出接口，方便切换映射方式而不影响下游材质逻辑
3. **OpenPBR 兼容**：内置 OpenPBR 标准的 Parent Material（`M_OpenPBR_Opaque_Parent`），对标新行业标准
4. **默认纹理资源**：提供一套预打包的默认纹理（黑白灰、平面法线、噪声），避免材质因缺少纹理而报错

目前处于 Beta 阶段（`IsBetaVersion=true`），是 Epic 在 UE 5.6+ 推出的新系统，预计将逐步替代各项目中分散的材质函数实现。

## 使用场景

- 你在做一个需要 Triplanar 映射的大世界场景（地形、岩石、山体）→ 使用 `ML_Triplanar_Parent` 或 `ML_DitherTriplanar_Parent` 作为材质 Layer
- 你需要在程序化网格上做无缝材质混合 → 使用 `MF_Coordinate_CellBombing` + `ML_CellBombUV_Parent`
- 你需要根据世界高度混合材质（雪线、草地、岩层）→ 使用 `MLB_WorldHeight` blend
- 你需要基于视角方向做材质混合（如雪只在朝上表面堆积）→ 使用 `MLB_DirectionalMask` 或 `MLB_ViewMask`
- 你希望材质图支持多种映射方式且可运行时切换 → `MF_ResolveCoordinateFrame_*` 提供统一接口，配合 `MF_Switch4_*` 节点做分支
- 你需要 Parallax Occlusion Mapping (POM) 效果 → 每种映射方式都有 `_POM` 后缀的 Layer 变体

## 蓝图用法

本插件为纯内容插件，不包含 C++ 源码和 BlueprintCallable 函数。所有功能通过 **材质编辑器（Material Editor）** 中的 Material Function 节点使用。

### 核心材质函数节点

#### 坐标映射（Coordinate）

| 函数 | 说明 |
|---|---|
| `MF_Coordinate_Triplanar` | 三平面映射，适合大型不规则网格 |
| `MF_Coordinate_Biplanar` | 双平面映射，性能更优的 Triplanar 替代 |
| `MF_Coordinate_CellBombing` | Cell Bombing 映射，程序化碎块化效果 |
| `MF_Coordinate_VariationUV` | UV 变体映射，基于随机化减少重复感 |
| `MF_Coordinate_Parallax` | 视差映射坐标偏移 |
| `MF_Coordinate_AnalyticalSphere` | 球体解析映射 |
| `MF_Coordinate_AnalyticalCapsule` | 胶囊体解析映射 |
| `MF_Coordinate_AnalyticalCylinder` | 圆柱体解析映射 |
| `MF_Coordinate_Keystone` | Keystone 变换映射 |
| `MF_Coordinate_Rand1/2/3` | 随机坐标生成（1D/2D/3D） |

#### 坐标帧解析（Resolve Coordinate Frame）

每种映射方式有 Basic / Dither / POM / DitherPOM 四种变体：

| 函数 | 说明 |
|---|---|
| `MF_ResolveCoordinateFrame_Triplanar_*` | Triplanar 帧解析（Basic / Dither / POM / DitherPOM） |
| `MF_ResolveCoordinateFrame_Biplanar_*` | Biplanar 帧解析 |
| `MF_ResolveCoordinateFrame_Octaplanar_*` | 八平面映射帧解析 |
| `MF_ResolveCoordinateFrame_HexTile_*` | 六角瓦片帧解析 |
| `MF_ResolveCoordinateFrame_CircleSplat_*` | 圆形 Splat 帧解析 |
| `MF_ResolveCoordinateFrame_CellBomb_*` | Cell Bomb 帧解析 |
| `MF_ResolveCoordinateFrame_TextureVariation_*` | 纹理变体帧解析 |
| `MF_ResolveCoordinateFrame_SimpleUV_*` | 简单 UV 帧解析 |
| `MF_ResolveCoordinateFrame_SphereUV_*` | 球面 UV 帧解析 |
| `MF_ResolveCoordinateFrame_CapsuleUV_*` | 胶囊 UV 帧解析 |
| `MF_ResolveCoordinateFrame_CylinderUV_*` | 圆柱 UV 帧解析 |
| `MF_ResolveCoordinateFrame_AxisProjection_*` | 轴投影帧解析 |

#### 混合与遮罩（Blend & Mask）

| 函数 | 说明 |
|---|---|
| `MF_Blend_HeightMask2/3` | 基于高度的 2/3 层遮罩 |
| `MF_Blend_RGBToIndex` | RGB 通道转索引 |
| `MF_Blend_CircleMask` | 圆形遮罩 |
| `MF_Blend_HexMask` | 六角遮罩 |
| `MF_Blend_TriplanarAxis` | Triplanar 轴向混合权重 |
| `MF_Mask_BandSelect` | 频带选择遮罩 |
| `MF_Mask_Directional` | 方向遮罩 |
| `MF_Mask_SDF` | SDF 遮罩 |
| `MF_Mask_View` | 视角遮罩 |

#### 工具函数（Utility）

| 函数 | 说明 |
|---|---|
| `MF_DeriveTangentBasis` | 派生切线空间基向量 |
| `MF_TangentNormal_OrientWorld` | 将切线法线转换为世界空间 |
| `MF_NormalStrength` | 法线强度调节 |
| `MF_Normal_Flatten` | 法线平坦化 |
| `MF_Rougness_Tweak` | 粗糙度微调 |
| `MF_Occlusion_Tweak` | 遮蔽微调 |
| `MF_DifColor_TransformHSV` | 漫反射颜色 HSV 变换 |
| `MF_Rotate2D` | 2D 旋转 |
| `MF_CoordinateTransform_2D` | 2D 坐标变换 |
| `MF_Compensated_Average` | 补偿平均值 |
| `MF_Hash42` | 42 哈希函数 |
| `MF_Noise_InterleavedGradientGolden_1d` | 交错梯度金色噪声 |
| `MF_Switch4_Vec2/Vec3` | 4 路 Vec2/Vec3 开关 |
| `MF_PrepareLWC` | 大世界坐标（LWC）准备 |
| `MF_SampleMaterial_TexFetchSingle/Double/Triple` | 纹理采样（1/2/3 纹理） |
| `MF_TexPointSample_RGB/NRM` | 点采样 RGB / 法线 |

### Material Layer 父材质（ML_）

提供可直接使用的 Material Layer 资产，每种坐标映射方案有普通版和 POM 版：

| Layer | 说明 |
|---|---|
| `ML_Triplanar_Parent` / `ML_TriplanarPOM_Parent` | 三平面映射 Layer |
| `ML_Biplanar_Parent` / `ML_BiplanarPOM_Parent` | 双平面映射 Layer |
| `ML_Octaplanar_Parent` / `ML_OctaplanarPOM_Parent` | 八平面映射 Layer |
| `ML_BasicUV_Parent` / `ML_BasicUVPOM_Parent` | 基础 UV Layer |
| `ML_HexTileUV_Parent` / `ML_HexTileUVPOM_Parent` | 六角瓦片 UV Layer |
| `ML_CircleSplatUV_Parent` / `ML_CircleSplatUVPOM_Parent` | 圆形 Splat UV Layer |
| `ML_CellBombUV_Parent` / `ML_CellBombUVPOM_Parent` | Cell Bomb UV Layer |
| `ML_TextureVariationUV_Parent` / `ML_TextureVariationUVPOM_Parent` | 纹理变体 UV Layer |
| `ML_CapsuleUV_Parent` / `ML_CapsuleUVPOM_Parent` | 胶囊 UV Layer |
| `ML_EllipsoidUV_Parent` / `ML_EllipsoidUVPOM_Parent` | 椭球 UV Layer |
| `ML_AxisProjection_Parent` / `ML_AxisProjectionPOM_Parent` | 轴投影 Layer |
| `ML_Dither*` | 上述所有 Layer 的 Dither 变体版本 |

### Material Layer Blends（MLB_）

| Blend | 说明 |
|---|---|
| `MLB_WorldHeight` | 基于世界高度混合材质层 |
| `MLB_DirectionalMask` | 基于法线方向的遮罩混合 |
| `MLB_ViewMask` | 基于视角的遮罩混合 |
| `MLB_UVTileMask` | 基于 UV 瓦片的遮罩混合 |
| `MLB_ShapeMask` | 形状遮罩混合 |
| `MLB_TextureMix` | 纹理混合 |
| `MLB_MeshPaint` | 网格绘制混合（Vertex Paint） |

### 使用示例（材质编辑器描述）

**示例 1：为岩石创建 Triplanar 材质**

1. 在材质编辑器中，右键搜索 `ML_Triplanar_Parent`，将其作为 Material Layer 引入
2. 连接 Base Color 纹理到 Layer 的 BaseColor 输入
3. 连接 Normal Map 到 Layer 的 Normal 输入
4. Layer 的输出自动连接到 Material Result
5. 如需 POM 效果，改用 `ML_TriplanarPOM_Parent`

**示例 2：使用 WorldHeight 混合草与岩石**

1. 创建两个 Material Layer：一个使用 `ML_Triplanar_Parent`（岩石），一个使用 `ML_BasicUV_Parent`（草地）
2. 添加 `MLB_WorldHeight` 作为 Blend
3. 调整 Height Blend 的过渡高度和过渡宽度
4. 在 Blend 节点上连接两个 Layer，输出到 Material Result

**示例 3：创建 Dither 混合效果**

1. 使用 `ML_DitherTriplanar_Parent` 替代 `ML_Triplanar_Parent`
2. Dither 变体通过屏幕空间抖动实现层间过渡，避免硬切割边
3. 适合需要柔和过渡的地表材质

## C++ 用法

本插件为纯内容插件，不包含 C++ 代码。无法通过 C++ 直接调用插件功能。

如果需要在 C++ 中使用这些材质函数，标准做法是：

1. 在材质编辑器中基于这些 Material Functions 创建材质
2. 在 C++ 中通过 `UMaterialInterface` / `UMaterialInstanceDynamic` 引用这些材质
3. 通过 `SetScalarParameterValue` / `SetVectorParameterValue` 动态调整参数

```cpp
// 标准的材质实例动态使用方式（非插件特有）
UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BaseMaterial, this);
MID->SetScalarParameterValue(FName("SomeParam"), Value);
MeshComponent->SetMaterial(0, MID);
```

## Demo 示例

由于是纯内容插件，无法提供编译示例。建议通过以下步骤体验：

1. 启用插件（默认已启用）
2. 创建新材质 → 在材质编辑器中右键搜索 `MF_Coordinate_Triplanar`
3. 创建 Material Layer → 搜索 `ML_Triplanar_Parent`
4. 连接默认纹理（插件自带的 `T_White_sRGB`、`T_FlatNorm_BC5` 等）到 Layer 输入
5. 切换不同映射方式（Biplanar / Octaplanar 等）观察效果差异

## 模块依赖

纯内容插件，无模块依赖。

你的项目 **不需要** 在 `Build.cs` 中添加任何依赖。只需确保插件已启用即可在材质编辑器中使用其资产。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-03 | `c4c0bd2` | Enable BaseMaterial Plugin by default. | 将插件从手动启用改为默认启用，表明 Epic 认为该插件已足够稳定 |
| 2025-08-03 | `b233691` | First push of new base material plugin. Contains a few example material functions/layers for sampling which will be iterated on, as well as a number of coordinate functions. | 首次提交，包含示例材质函数/采样层和多种坐标函数 |

### 维护评价

- **创建时间**：2025-08-03，不到 1 年历史，非常新的插件
- **更新频率**：仅 2 次提交，功能稳定但仍在早期阶段
- **Beta 状态**：`IsBetaVersion=true`，API 和资产结构可能会变化
- **默认启用**：已设为默认启用，说明 Epic 对其稳定性有信心
- **活跃维护**：作为 UE 5.6+ 的新系统，预计会随引擎版本持续迭代
- **建议**：可以在新项目中试用，但注意 Beta 标签意味着资产名称和结构可能在后续版本中变更。暂不建议在需要长期稳定的生产环境中重度依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/BaseMaterial)
- 官方文档：暂无（DocsURL 为空）
- 测试用例：无（纯内容插件，无自动化测试）
