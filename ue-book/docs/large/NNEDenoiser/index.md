# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（OIDN 神经网络模型、IO 映射表、降噪器资产） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是（IsBetaVersion=true） |
| 创建时间 | 2023-11-20 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 是 UE5 路径追踪器（Path Tracer）的 **AI 降噪插件**。它利用 NNE（Neural Network Engine）框架运行神经网络模型，在路径追踪渲染的低采样率噪声图像上执行实时降噪，从而在保持画面质量的前提下大幅减少所需的采样数。

核心解决的问题：路径追踪渲染需要大量采样才能收敛到低噪声画面，但实时交互场景无法承受高采样率的性能开销。NNEDenoiser 通过 OIDN（Intel Open Image Denoise）2.3 系列模型，以深度学习方式从少量采样的噪声图像中恢复出干净画面。

插件支持两种降噪模式：
- **空间降噪（Spatial）**：仅利用当前帧的 Color、Albedo、Normal 等 G-Buffer 信息进行单帧降噪
- **时空降噪（Spatial-Temporal）**：额外利用前一帧的降噪结果和光流（Flow）信息进行时序累积，获得更稳定的降噪效果

## 使用场景

- 你在使用 UE5 Path Tracer 做建筑可视化 / 产品渲染，希望在编辑器中实时预览时减少噪声 → 启用 NNEDenoiser（默认已启用）
- 你需要在不同硬件上灵活切换降噪后端 → 通过 `NNEDenoiser.Runtime.Type` 在 CPU/GPU/RDG 之间切换
- 你的渲染分辨率超过了神经网络模型的输入尺寸 → 插件的 Tiling 系统自动将画面分块处理
- 你需要支持 Alpha 通道的降噪 → 使用带 Alpha 后缀的资产变体
- 你需要时序稳定的降噪结果（如动画序列渲染）→ 配置 Temporal Denoiser Asset

## 蓝图用法

NNEDenoiser 没有暴露任何 BlueprintCallable 节点。它是一个纯渲染管线集成插件，通过以下方式配置：

### 项目设置（Project Settings > Plugins > NNE Denoiser）

| 设置项 | 说明 | 默认值 |
|---|---|---|
| Denoiser Asset | 选择空间降噪器的资产 | `NNED_Oidn2-3_Balanced_Alpha` |
| Maximum Tile Size Override | 覆盖资产定义的最大分块大小（-1 = 不覆盖） | -1 |
| Runtime Type | 推理后端类型（CPU/GPU/RDG） | RDG |
| Runtime Name Override | 指定具体的运行时名称（留空使用默认） | 空 |

### 控制台变量

| CVar | 类型 | 说明 |
|---|---|---|
| `NNEDenoiser` | bool | 启用/禁用降噪器 |
| `NNEDenoiser.Asset` | int | 选择降噪资产（0=使用项目设置，1-6=预设资产） |
| `NNEDenoiser.TemporalAsset` | int | 选择时序降噪资产（0=使用项目设置，1-2=预设资产） |
| `NNEDenoiser.Runtime.Type` | int | 运行时类型（0=CPU，1=GPU，2=RDG） |
| `NNEDenoiser.Runtime.Name` | string | 运行时名称覆盖 |

`NNEDenoiser.Asset` 预设值：

| 值 | 资产 |
|---|---|
| 1 | OIDN Fast |
| 2 | OIDN Balanced |
| 3 | OIDN High Quality |
| 4 | OIDN Fast + Alpha |
| 5 | OIDN Balanced + Alpha |
| 6 | OIDN High Quality + Alpha |

## C++ 用法

NNEDenoiser 主要通过渲染管线集成工作，不提供面向外部的 C++ API。以下是从源码中提取的内部架构和关键类。

### 架构总览

```
FViewExtension (SceneViewExtension)
  ├─ 监听 Path Tracer 激活状态
  ├─ 从 Settings/CVar 读取降噪器配置
  ├─ 创建 FPathTracingDenoiser (空间降噪器)
  └─ 创建 FPathTracingSpatialTemporalDenoiser (时空降噪器)
        │
        └─ FGenericDenoiser (核心降噪逻辑)
              ├─ IModelInstance (NNE 模型实例)
              │   ├─ FModelInstanceCPU
              │   ├─ FModelInstanceGPU
              │   └─ FModelInstanceRDG
              ├─ IInputProcess / FInputProcessBase (输入预处理)
              ├─ IOutputProcess / FOutputProcessBase (输出后处理)
              ├─ IAutoExposure / FAutoExposure (自动曝光)
              ├─ ITransferFunction / Oidn::FTransferFunction (传输函数)
              └─ FTiling (分块系统)
```

### 核心类说明

#### 数据资产

| 类 | 文件 | 说明 |
|---|---|---|
| `UNNEDenoiserAsset` | `Public/NNEDenoiserAsset.h` | 空间降噪器数据资产，包含 NNE 模型数据、IO 映射表和分块配置 |
| `UNNEDenoiserTemporalAsset` | `Public/NNEDenoiserTemporalAsset.h` | 时空降噪器数据资产，结构与 UNNEDenoiserAsset 类似 |
| `UNNEDenoiserSettings` | `Public/NNEDenoiserSettings.h` | 项目设置类，backed by CVars |

#### IO 映射系统

| 类 | 文件 | 说明 |
|---|---|---|
| `FNNEDenoiserInputMappingData` | `Public/NNEDenoiserIOMappingData.h` | 输入映射表行结构，定义资源（Color/Albedo/Normal/Output）到 Tensor 的通道映射 |
| `FNNEDenoiserOutputMappingData` | `Public/NNEDenoiserIOMappingData.h` | 输出映射表行结构 |
| `FNNEDenoiserTemporalInputMappingData` | `Public/NNEDenoiserIOMappingData.h` | 时序输入映射，额外支持 Flow 资源和 FrameIndex |
| `FResourceMapping` | `Private/NNEDenoiserResourceMapping.h` | 运行时资源映射，将 Tensor 通道映射到渲染资源通道 |
| `FResourceMappingList` | `Private/NNEDenoiserResourceMapping.h` | 多 Tensor 的资源映射列表 |

#### 分块系统

| 类 | 文件 | 说明 |
|---|---|---|
| `FTilingConfig` | `Public/NNEDenoiserTilingConfig.h` | 分块配置（Alignment、Overlap、MaxSize、MinSize） |
| `FTiling` | `Private/NNEDenoiserTiling.h` | 运行时分块结果，包含 TileSize、Count 和 Tiles 数组 |
| `FTile` | `Private/NNEDenoiserTiling.h` | 单个分块，包含 Position 和 Input/Output Offsets |

#### 模型实例

| 类 | 文件 | 说明 |
|---|---|---|
| `IModelInstance` | `Private/NNEDenoiserModelInstance.h` | 模型实例接口，继承自 `NNE::IModelInstanceRDG` |
| `FModelInstanceCPU` | `Private/NNEDenoiserModelInstanceCPU.h` | CPU 运行时模型实例（使用 NNERuntimeORTCpu） |
| `FModelInstanceGPU` | `Private/NNEDenoiserModelInstanceGPU.h` | GPU 运行时模型实例（使用 NNERuntimeORTDml） |
| `FModelInstanceRDG` | `Private/NNEDenoiserModelInstanceRDG.h` | RDG 运行时模型实例（使用 NNERuntimeORTDml 或 NNERuntimeRDGHlsl） |

#### IO 处理

| 类 | 文件 | 说明 |
|---|---|---|
| `IInputProcess` | `Private/NNEDenoiserIOProcess.h` | 输入处理接口 |
| `IOutputProcess` | `Private/NNEDenoiserIOProcess.h` | 输出处理接口 |
| `FInputProcessBase` | `Private/NNEDenoiserIOProcessBase.h` | 基础输入处理实现，负责将渲染资源写入 Tensor Buffer |
| `FOutputProcessBase` | `Private/NNEDenoiserIOProcessBase.h` | 基础输出处理实现，负责从 Tensor Buffer 读取结果到输出纹理 |

#### 传输函数与自动曝光

| 类 | 文件 | 说明 |
|---|---|---|
| `ITransferFunction` | `Private/NNEDenoiserTransferFunction.h` | 传输函数接口，支持 CPU 和 RDG 两种执行路径 |
| `Oidn::FTransferFunction` | `Private/NNEDenoiserTransferFunctionOidn.h` | OIDN 传输函数实现（Forward/Inverse 变换） |
| `IAutoExposure` | `Private/NNEDenoiserAutoExposure.h` | 自动曝光接口 |
| `FAutoExposure` | `Private/NNEDenoiserAutoExposure.h` | 自动曝光实现，计算 HDR 输入的曝光缩放因子 |

#### 降噪器入口

| 类 | 文件 | 说明 |
|---|---|---|
| `FViewExtension` | `Private/NNEDenoiserViewExtension.h` | SceneViewExtension，负责监听 Path Tracer 状态并注册/注销降噪器 |
| `FGenericDenoiser` | `Private/NNEDenoiserGenericDenoiser.h` | 核心降噪逻辑，管理 Tiling、模型推理和 IO 处理的完整流程 |
| `FPathTracingDenoiser` | `Private/NNEDenoiserPathTracingDenoiser.h` | 实现 `IPathTracingDenoiser` 接口（空间降噪） |
| `FPathTracingSpatialTemporalDenoiser` | `Private/NNEDenoiserPathTracingSpatialTemporalDenoiser.h` | 实现 `IPathTracingSpatialTemporalDenoiser` 接口（时空降噪） |
| `FHistory` | `Private/NNEDenoiserHistory.h` | 时序历史记录，存储前几帧的渲染资源用于时序降噪 |

#### GPU Shader（NNEDenoiserShaders 模块）

| 类 | 文件 | 说明 |
|---|---|---|
| `FAutoExposureDownsampleCS` | `Internal/NNEDenoiserShadersAutoExposureCS.h` | 自动曝光降采样 Compute Shader |
| `FAutoExposureReduceCS` | `Internal/NNEDenoiserShadersAutoExposureCS.h` | 自动曝光归约 Compute Shader |
| `FAutoExposureReduceFinalCS` | `Internal/NNEDenoiserShadersAutoExposureCS.h` | 自动曝光最终归约 Compute Shader |
| `FTransferFunctionOidnCS` | `Internal/NNEDenoiserShadersTransferFunctionOidnCS.h` | OIDN 传输函数 Compute Shader（Forward/Inverse） |
| `FDefaultIOProcessCS` | `Internal/NNEDenoiserShadersDefaultIOProcessCS.h` | 默认 IO 处理 Compute Shader |
| `FMappedCopyCS` | `Internal/NNEDenoiserShadersMappedCopyCS.h` | 映射拷贝 Compute Shader |

### 降噪流程

```
1. FViewExtension::BeginRenderViewFamily()
   - 检测 Path Tracer 是否激活
   - 检查配置是否变化
   - 如需更新，创建新的 FGenericDenoiser

2. FViewExtension::PreRenderViewFamily_RenderThread()
   - 在渲染线程注册降噪器到 Path Tracer 管线

3. FGenericDenoiser::AddPasses() (每帧调用)
   a. Prepare(): 根据视口大小计算 Tiling
   b. 创建 InputBuffers / OutputBuffers (RDG Buffer)
   c. 计算 AutoExposure（如使用 OIDN 模型）
   d. 对每个 Tile:
      - InputProcess: 将渲染资源写入 InputBuffers
      - ModelInstance.EnqueueRDG(): 执行神经网络推理
      - OutputProcess: 从 OutputBuffers 写回输出纹理
   e. 返回 History（用于时序降噪的帧间数据）
```

### 运行时回退机制

当指定的运行时不可用时，插件会按优先级回退：

```
RDG 模式: NNERuntimeORTDml → NNERuntimeRDGHlsl → NNERuntimeORTDml(GPU) → NNERuntimeORTCpu(CPU)
GPU 模式: NNERuntimeORTDml → NNERuntimeORTCpu(CPU)
CPU 模式: NNERuntimeORTCpu
```

### 预置资产

插件 Content 目录包含以下预置资产：

**空间降噪器（NNED_ 前缀）**：
| 资产 | 模型 | 说明 |
|---|---|---|
| `NNED_Oidn2-3_Fast` | OIDN 2.3 RT HDR (small) | 快速模式，无 Alpha |
| `NNED_Oidn2-3_Balanced` | OIDN 2.3 RT HDR (default) | 平衡模式，无 Alpha |
| `NNED_Oidn2-3_HighQuality` | OIDN 2.3 RT HDR (large) | 高质量模式，无 Alpha |
| `NNED_Oidn2-3_Fast_Alpha` | OIDN 2.3 RT HDR (small) + Alpha | 快速模式，含 Alpha |
| `NNED_Oidn2-3_Balanced_Alpha` | OIDN 2.3 RT HDR (default) + Alpha | 平衡模式，含 Alpha（**默认**） |
| `NNED_Oidn2-3_HighQuality_Alpha` | OIDN 2.3 RT HDR (large) + Alpha | 高质量模式，含 Alpha |

**时空降噪器（NNEDT_ 前缀）**：
| 资产 | 说明 |
|---|---|
| `NNEDT_Oidn2-3_Balanced` | 平衡模式时序降噪，无 Alpha |
| `NNEDT_Oidn2-3_Balanced_Alpha` | 平衡模式时序降噪，含 Alpha（**默认**） |

**IO 映射表**：
| 资产 | 说明 |
|---|---|
| `NNEDIM_ColorAlbedoNormal_Default` | 标准输入映射（Color + Albedo + Normal） |
| `NNEDIM_ColorAlbedoNormal_Alpha` | 含 Alpha 的输入映射 |
| `NNEDIM_HighQuality_Default` | 高质量输入映射 |
| `NNEDIM_HighQuality_Alpha` | 高质量含 Alpha 输入映射 |
| `NNEDOM_Output_Default` | 标准输出映射 |
| `NNEDOM_Output_Alpha` | 含 Alpha 的输出映射 |
| `NNEDTIM_ColorAlbedoNormal_Default` | 时序标准输入映射 |
| `NNEDTIM_ColorAlbedoNormal_Alpha` | 时序含 Alpha 输入映射 |
| `NNEDTOM_Output_Default` | 时序标准输出映射 |
| `NNEDTOM_Output_Alpha` | 时序含 Alpha 输出映射 |

## Demo 示例

NNEDenoiser 是一个管线集成插件，不需要编写代码即可使用。以下是启用和配置步骤：

### 基本使用

1. 确保插件已启用（默认已启用）
2. 在项目设置中选择降噪资产：Project Settings > Plugins > NNE Denoiser > Denoiser Asset
3. 在视口中启用 Path Tracer：Show > Path Tracing
4. 降噪器会自动激活并处理 Path Tracer 输出

### 通过控制台调整

```cpp
// 在代码或控制台中切换降噪模式
// 切换到快速模式
auto* Settings = GetMutableDefault<UNNEDenoiserSettings>();
Settings->DenoiserAsset = FSoftObjectPath(TEXT("/NNEDenoiser/NNED_Oidn2-3_Fast.NNED_Oidn2-3_Fast"));

// 或通过 CVar
IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Asset"))->Set(1); // OIDN Fast
IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Type"))->Set(0); // CPU
```

### 自定义降噪器资产

如需创建自定义降噪器，需要：

1. **准备 NNE 模型数据**：导入 ONNX 格式的降噪模型为 `UNNEModelData` 资产
2. **创建 IO 映射表**：创建 DataTable 定义输入/输出的资源到 Tensor 通道映射
3. **创建降噪器资产**：创建 `UNNEDenoiserAsset`，配置 ModelData、InputMapping、OutputMapping 和 TilingConfig
4. **在项目设置中引用**：将自定义资产设置为 Denoiser Asset

## 模块依赖

### NNEDenoiser 模块

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `RenderCore` | 渲染核心（RDG、纹理管理等） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `DeveloperSettings` | 开发者设置基类（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |
| `NNE` | Neural Network Engine 框架（私有依赖） |
| `NNEDenoiserShaders` | 本插件的 Shader 模块（私有依赖） |
| `Renderer` | 渲染器（Path Tracer 集成）（私有依赖） |
| `RHI` | 渲染硬件接口（私有依赖） |

### NNEDenoiserShaders 模块

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `RenderCore` | 渲染核心 |
| `Projects` | 项目管理（私有依赖） |
| `Renderer` | 渲染器（私有依赖） |
| `RHI` | 渲染硬件接口（私有依赖） |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `NNERuntimeORT` | ONNX Runtime NNE 后端，提供 CPU/GPU/RDG 推理能力 |

## 维护状态

### 近期更新

1. **2025-06-26** `a2e7518` — 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏
   - 全局性代码清理，使用 UnrealCodeFixup 工具自动应用，无功能变化

2. **2025-04-23** `6ae5733` — 转换为 dllstorage 方式
   - 全局性构建系统变更，将方法/静态变量的导出从类型级改为声明级，无功能变化

3. **2024-12-18** `6ed576a` — 修复 FormatStringSan 警告
   - 修复 `%d` 打印 `TCHAR*` 的格式化问题，属于代码质量改进

4. **2024-12-13** `e0864c2` — 修复多视口场景下的降噪器行为
   - **实质性改进**：更谨慎地处理多个视口中并非全部使用 Path Tracer 的情况，避免每帧加载/卸载降噪器

5. **2024-12-03** `ab39869` — 添加最大分块大小覆盖设置
   - **实质性改进**：新增 `MaximumTileSizeOverride` 设置，允许全局覆盖降噪资产定义的最大分块大小，可减少 GPU 内存占用

### 维护评价

- **创建时间**：2023 年 11 月（Experimental），2024 年 8 月移至正式目录
- **最近更新**：2025 年 6 月，但多为全局性代码清理，最近的功能性更新在 2024 年 12 月
- **维护状态**：维护中 — 核心功能稳定，随引擎版本进行常规维护
- **Beta 状态**：IsBetaVersion=true，API 和行为可能在后续版本中变化
- **已知限制**：
  - 仅支持 Win64、Linux、Mac 平台
  - 依赖 NNERuntimeORT 插件（ONNX Runtime）
  - 时序降噪器目前标记为"Currently not used"（TemporalDenoiserAsset 在设置中被隐藏）
  - 需要 Ray Tracing 启用才能工作
- **推荐程度**：✅ 推荐在使用 Path Tracer 的场景中使用，这是 Epic 官方提供的降噪方案，开箱即用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NNE/NNEDenoiser)
- [NNERuntimeORT 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NNE/NNERuntimeORT) — 本插件的运行时依赖
- [NNE 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NNE/NNE) — Neural Network Engine 框架
- [Intel Open Image Denoise](https://www.openimagedenoise.org/) — 本插件使用的 OIDN 模型来源
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/NNE/NNEDenoiser/Source/NNEDenoiser/Private/NNEDenoiserUnitTests.cpp) — AutoExposure 单元测试
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/NNE/NNEDenoiser/Source/NNEDenoiser/Private/NNEDenoiserUnitTestOidn.cpp) — OIDN 传输函数单元测试
