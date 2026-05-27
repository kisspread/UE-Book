# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据资产蓝图类、着色器） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 是一个基于 NNE（Neural Network Engine）框架的**神经网络路径追踪降噪器**。它解决了路径追踪渲染中噪点过多需要大量采样才能获得清晰图像的问题——通过在少量采样后使用神经网络模型对渲染结果进行智能去噪，大幅减少获得高质量图像所需的渲染时间。

该插件的核心能力包括：

1. **多运行时支持**：可在 CPU、GPU、RDG 三种后端上执行神经网络推理，适配不同硬件条件
2. **分块处理（Tiling）**：支持将大分辨率图像分割为小块分别降噪，降低 GPU 显存占用
3. **空间与时空降噪**：同时支持单帧空间降噪和利用运动向量的多帧时空降噪
4. **灵活的 I/O 映射**：通过数据表（DataTable）配置神经网络张量与渲染资源（颜色、法线、反照率等）之间的通道映射
5. **传输函数**：内置 OIDN 风格的 HDR 传输函数，在降噪前后对图像进行归一化处理

该插件从 Experimental 文件夹迁移到正式位置，标记为 Beta 状态，说明 Epic 认为其核心功能已经可用但仍在打磨中。

## 使用场景

- 你使用 UE5 路径追踪器（Path Tracer）进行产品级渲染 → 用 NNEDenoiser 加速去噪
- 你需要在电影/建筑可视化中减少渲染时间 → 配置降噪资产后路径追踪器自动使用
- 你训练了自定义的 ONNX 降噪模型 → 通过 `UNNEDenoiserAsset` 导入并配置映射关系
- 你需要在高分辨率下使用降噪但 GPU 显存不足 → 配置 `TilingConfig` 的 `MaxSize` 进行分块处理
- 你需要利用时间信息进行多帧降噪（Motion Vectors）→ 使用 `UNNEDenoiserTemporalAsset`

## 蓝图用法

NNEDenoiser 主要通过**数据资产**和**项目设置**进行配置，而非直接暴露蓝图函数节点。其工作方式是：创建配置资产 → 在设置中引用 → 路径追踪器自动集成。

### 核心资产类型

| 资产类 | 说明 | 所在类 |
|---|---|---|
| `NNEDenoiserAsset` | 空间降噪器配置资产 | `UNNEDenoiserAsset` |
| `NNEDenoiserTemporalAsset` | 时空降噪器配置资产 | `UNNEDenoiserTemporalAsset` |

### 配置数据结构

| 结构体 | 说明 | 所在类 |
|---|---|---|
| `FNNEDenoiserInputMappingData` | 输入映射行（张量↔资源通道映射） | `UNNEDenoiserAsset::InputMapping` 表 |
| `FNNEDenoiserOutputMappingData` | 输出映射行 | `UNNEDenoiserAsset::OutputMapping` 表 |
| `FNNEDenoiserTemporalInputMappingData` | 时序输入映射行（含 FrameIndex） | `UNNEDenoiserTemporalAsset::InputMapping` 表 |
| `FNNEDenoiserTemporalOutputMappingData` | 时序输出映射行 | `UNNEDenoiserTemporalAsset::OutputMapping` 表 |
| `FTilingConfig` | 分块配置（对齐、重叠、最大/最小块大小） | 内嵌于资产 |

### 使用示例（资产配置流程）

1. **准备 NNE 模型数据资产**：导入 ONNX 降噪模型为 `UNNEModelData` 资产
2. **创建输入映射表**：新建 `DataTable`，行结构选 `NNEDenoiserInputMappingData`，配置张量通道到渲染资源的映射（Color、Albedo、Normal 等）
3. **创建输出映射表**：同理，行结构选 `NNEDenoiserOutputMappingData`
4. **创建降噪器资产**：新建 `NNEDenoiserAsset`，引用模型数据、输入/输出映射表，配置 TilingConfig
5. **在项目设置中启用**：导航到 Project Settings → Rendering → NNE Denoiser，指定刚创建的资产

### 关键枚举

| 枚举 | 说明 | 可选值 |
|---|---|---|
| `EDenoiserRuntimeType` | 推理运行时 | `CPU`, `GPU`, `RDG` |
| `EInputResourceName` | 空间降噪输入资源 | `Color`, `Albedo`, `Normal`, `Output` |
| `ETemporalInputResourceName` | 时空降噪输入资源 | `Color`, `Albedo`, `Normal`, `Flow`, `Output` |
| `EResourceName` | 内部资源标识 | `Color`, `Albedo`, `Normal`, `Flow`, `Output` |

## C++ 用法

NNEDenoiser 主要作为**内部引擎系统**运行，对开发者开放的 C++ API 有限。以下是从源码中提取的关键用法。

### 头文件引入

```cpp
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserSettings.h"
#include "NNEDenoiserIOMappingData.h"
#include "NNEDenoiserTilingConfig.h"
```

### 基本用法：程序化配置降噪器资产

从 `Public/NNEDenoiserAsset.h` 和 `Public/NNEDenoiserIOMappingData.h` 提取。

```cpp
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserIOMappingData.h"
#include "NNEDenoiserTilingConfig.h"

// 创建降噪器资产
UNNEDenoiserAsset* DenoiserAsset = NewObject<UNNEDenoiserAsset>();

// 引用 NNE 模型数据
DenoiserAsset->ModelData = SoftModelDataPath; // TSoftObjectPtr<UNNEModelData>

// 引用输入映射表（DataTable 行结构为 FNNEDenoiserInputMappingData）
DenoiserAsset->InputMapping = SoftInputMappingPath;

// 引用输出映射表
DenoiserAsset->OutputMapping = SoftOutputMappingPath;

// 配置分块参数
DenoiserAsset->TilingConfig.Alignment = 64;
DenoiserAsset->TilingConfig.Overlap = 32;
DenoiserAsset->TilingConfig.MaxSize = 1024;
DenoiserAsset->TilingConfig.MinSize = 64;
```

### 基本用法：配置降噪器设置

从 `Public/NNEDenoiserSettings.h` 提取。

```cpp
#include "NNEDenoiserSettings.h"

// 获取降噪器设置（Config = Engine）
UNNEDenoiserSettings* Settings = GetMutableDefault<UNNEDenoiserSettings>();

// 设置降噪器资产
Settings->DenoiserAsset = SoftDenoiserAssetPath;

// 覆盖最大分块大小（-1 表示不覆盖）
Settings->MaximumTileSizeOverride = 512;

// 通过 CVar 切换运行时类型
// NNEDenoiser.Runtime.Type = 0 (CPU), 1 (GPU), 2 (RDG)
// NNEDenoiser.Runtime.Name = "ONNX" (可选，指定运行时名称)
```

### 进阶用法：扩展自定义传输函数

从 `Private/NNEDenoiserTransferFunction.h` 和 `Private/NNEDenoiserTransferFunctionOidn.h` 提取。OIDN 传输函数可作为自定义实现的参考。

```cpp
#include "NNEDenoiserTransferFunction.h"

// 实现自定义传输函数接口
class FMyTransferFunction : public ITransferFunction
{
public:
    // 前向变换：将 HDR 图像归一化到神经网络友好的范围
    void Forward(TConstArrayView<FLinearColor> InputImage, float InputScale,
                 TArray<FLinearColor>& OutputImage) const override
    {
        OutputImage.SetNumUninitialized(InputImage.Num());
        for (int32 i = 0; i < InputImage.Num(); ++i)
        {
            // 自定义归一化逻辑
            OutputImage[i] = InputImage[i] * InputScale;
        }
    }

    // 逆向变换：将神经网络输出恢复为 HDR 范围
    void Inverse(TConstArrayView<FLinearColor> InputImage, float InvInputScale,
                 TArray<FLinearColor>& OutputImage) const override
    {
        OutputImage.SetNumUninitialized(InputImage.Num());
        for (int32 i = 0; i < InputImage.Num(); ++i)
        {
            OutputImage[i] = InputImage[i] * InvInputScale;
        }
    }

    // RDG 版本的前向变换（GPU 路径）
    void RDGSetInputScale(FRDGBufferRef InInputScaleBuffer) override
    {
        InputScaleBuffer = InInputScaleBuffer;
    }

    void RDGForward(FRDGBuilder& GraphBuilder,
                    FRDGTextureRef InputTexture,
                    FRDGTextureRef OutputTexture) const override
    {
        // 实现 RDG compute shader 版本的前向变换
        // 参考 NNEDenoiserTransferFunctionOidn 中的实现
    }

    void RDGInverse(FRDGBuilder& GraphBuilder,
                    FRDGTextureRef InputTexture,
                    FRDGTextureRef OutputTexture) const override
    {
        // 实现 RDG compute shader 版本的逆向变换
    }

private:
    FRDGBufferRef InputScaleBuffer{};
};
```

## Demo 示例

以下示例展示如何创建一个最小的降噪器配置，引用已有模型数据并设置到引擎中。

```cpp
// NNEDenoiserSetup.h
#pragma once

#include "CoreMinimal.h"

class UNNEModelData;
class UDataTable;

class FNNEDenoiserSetup
{
public:
    /**
     * 创建并配置一个基本的降噪器资产
     * @param ModelData     - 已导入的 ONNX 降噪模型数据资产
     * @param InputTable    - 输入映射 DataTable（行结构为 FNNEDenoiserInputMappingData）
     * @param OutputTable   - 输出映射 DataTable（行结构为 FNNEDenoiserOutputMappingData）
     * @return 创建的降噪器资产，调用者负责管理生命周期
     */
    static UNNEDenoiserAsset* CreateDenoiserAsset(
        UNNEModelData* ModelData,
        UDataTable* InputTable,
        UDataTable* OutputTable);

    /**
     * 将降噪器资产应用到引擎设置中
     */
    static void ApplyToSettings(UNNEDenoiserAsset* Asset);
};
```

```cpp
// NNEDenoiserSetup.cpp
#include "NNEDenoiserSetup.h"

#include "NNEDenoiserAsset.h"
#include "NNEDenoiserSettings.h"
#include "NNEDenoiserIOMappingData.h"
#include "NNEModelData.h"
#include "Engine/DataTable.h"

UNNEDenoiserAsset* FNNEDenoiserSetup::CreateDenoiserAsset(
    UNNEModelData* ModelData,
    UDataTable* InputTable,
    UDataTable* OutputTable)
{
    check(ModelData);
    check(InputTable);
    check(OutputTable);

    UNNEDenoiserAsset* Asset = NewObject<UNNEDenoiserAsset>();

    // 关联模型数据
    Asset->ModelData = ModelData;

    // 关联映射表
    Asset->InputMapping = InputTable;
    Asset->OutputMapping = OutputTable;

    // 配置分块参数：64 对齐，32 重叠，最大 512，最小 64
    Asset->TilingConfig.Alignment = 64;
    Asset->TilingConfig.Overlap = 32;
    Asset->TilingConfig.MaxSize = 512;
    Asset->TilingConfig.MinSize = 64;

    return Asset;
}

void FNNEDenoiserSetup::ApplyToSettings(UNNEDenoiserAsset* Asset)
{
    UNNEDenoiserSettings* Settings = GetMutableDefault<UNNEDenoiserSettings>();
    Settings->DenoiserAsset = Asset;
    Settings->PostInitProperties();
}
```

## 模块依赖

从 Build.cs 分析，NNEDenoiser 模块的依赖如下：

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine 核心框架，提供模型实例化和推理接口 |
| `NNERuntimeORT` | ONNX Runtime 后端（plugin 依赖声明），实际执行 ONNX 模型推理 |
| `RenderCore` | RDG (Render Dependency Graph) 框架、Pooled Render Target |
| `RHI` | GPU 纹理/Buffer 的底层读写操作 |
| `RHICore` | RHI 辅助功能 |
| `Renderer` | 路径追踪降噪器接口（IPathTracingDenoiser, IPathTracingSpatialTemporalDenoiser） |
| `NNEDenoiserShaders` | 本插件的着色器模块（数据拷贝、传输函数的 Compute Shader） |

> 注意：该插件**强依赖** `NNERuntimeORT` 插件（在 .uplugin 的 Plugins 字段中声明），需要该插件启用才能工作。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一 GPU 同步 API，替换废弃的阻塞调用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充缺失的渲染头文件包含和前向声明 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分头文件，减少编译依赖 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前批量替换导致的错误 |

### 维护评价

- **年龄**：约 1.6 年，相对较新的插件
- **状态**：Beta 版本，从 Experimental 迁移至正式目录
- **活跃度**：近期（2026-02 至 2026-04）有多次更新，但均为**编译维护和代码清理**（头文件拆分、API 迁移、错误修复），未见功能性增强
- **依赖**：强依赖 `NNERuntimeORT` 插件，如果该插件不可用则无法工作
- **平台**：支持 Win64、Linux、Mac
- **已知限制**：Beta 状态，API 可能变更；`TemporalDenoiserAsset` 字段在设置中被标记为隐藏（Currently not used）

**推荐程度**：如果你使用 UE5 路径追踪器并需要降噪，这是官方推荐方案，可以使用但需注意 Beta 状态意味着接口可能变动。对于生产环境建议做好版本隔离。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- 官方文档（暂无）