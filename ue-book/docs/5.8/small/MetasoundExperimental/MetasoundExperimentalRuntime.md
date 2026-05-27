# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | Metasounds 实验性扩展 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 节点资产、示例配置） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

本插件是 MetaSound 系统的实验性扩展，核心功能是引入 **CAT（Channel Agnostic Type，通道无关类型）** 音频处理框架。

传统 MetaSound 节点在设计时就锁定了通道格式（如 Mono、Stereo、5.1），这导致同一套 MetaSound 图无法灵活适配不同的输出通道配置。CAT 系统通过抽象通道布局，让 MetaSound 图在运行时动态地进行通道格式转换、混合和声像处理，无需预先知道具体的通道数量和布局。

具体解决的问题：
- **跨格式音频处理**：同一个 MetaSound 图可以在 Mono 输出设备和 7.1 环绕声设备上无缝运行
- **动态通道转换**：在图内部实时进行格式转换（如 Stereo→5.1），支持上混/下混策略配置
- **多输入混合**：将不同通道格式的音频输入混合为统一格式输出
- **声像控制**：基于方位角的 CAT 声像处理，支持等功率和线性两种映射方法

该插件从 Epic 内部的 NotForLicensees 目录迁出，属于开发中的新特性，尚未稳定。

## 使用场景

- 你需要构建一个 **通用音频处理图**，希望它同时适配耳机（Stereo）和家庭影院（7.1）→ 用 CAT 节点替代固定格式节点
- 你需要在 MetaSound 图中 **动态混合多个不同通道格式的音频源** → 用 CatMixer 节点
- 你需要在图中 **临时转换通道格式** 后再进行其他处理 → 用 CatCasting 节点
- 你需要将通道无关的音频 **声像分配到特定的空间布局**（如 Stereo 或 Quad）→ 用 CatPanner 节点
- 你正在为 MetaSound 开发新的 **可配置自定义节点**，需要参考示例 → 查看 ExampleNode 配置模板

## 蓝图用法

本插件的节点主要通过 MetaSound 编辑器中的节点面板访问，不直接暴露为常规蓝图节点。以下是节点配置层面的可用属性和选项。

### 核心配置选项

#### 格式选择辅助类

| 方法 | 说明 | 所在类 |
|---|---|---|
| `GetCastingOptions` | 获取所有可用的 CAT 格式选项 | `UMetasoundCatCastingOptionsHelper` |
| `GetCastingOptions_NoAbstract` | 获取非抽象格式选项（排除声场、高阶Ambisonics） | `UMetasoundCatCastingOptionsHelper` |
| `GetCastingOptions_DiscreteOnly` | 仅离散格式（兼容 Mixer 的格式） | `UMetasoundCatCastingOptionsHelper` |
| `GetCastingOptions_AudioMixerOnly` | 仅标准 AudioMixer 格式：Mono、Stereo、Quad、5.1、7.1 | `UMetasoundCatCastingOptionsHelper` |
| `GetAzimuthalChannelOptions` | 获取方位角离散通道选项 | `UMetasoundCatAzimuthalChannelOptionsHelper` |

#### CatCasting 节点配置

在 MetaSound 编辑器中放置 CatCasting 节点后，可配置：

| 属性 | 类型 | 说明 |
|---|---|---|
| ToType | FName | 目标输出格式（如 Mono、Stereo2Dot0） |
| TranscodeMethod | EMetasoundCatCastingMethod | 转码方法：ChannelDrop（丢弃通道）或 MixUpOrDown（上下混） |
| MixMethod | EMetasoundChannelMapMonoUpmixMethod | 上混方法（仅 MixUpOrDown 时可用）：Linear、EqualPower、FullVolume |

#### CatMixer 节点配置

| 属性 | 类型 | 说明 |
|---|---|---|
| FormatChoosingMethod | EMetasoundMixerFormatChoosingMethod | 输出格式决策：HighestInput / LowestInput / MetasoundOutput / Custom |
| CatCastingMethod | EMetasoundCatCastingMethod | 转码方法 |
| ChannelMapMonoUpmixMethod | EMetasoundChannelMapMonoUpmixMethod | 上混方法 |
| CustomMixFormat | FName | 自定义混合格式（仅 Custom 时可用） |
| NumInputs | int32 | 输入数量（1-100） |

#### CatPanner 节点配置

| 属性 | 类型 | 说明 |
|---|---|---|
| PanToType | FName | 目标输出通道类型（仅方位角离散格式） |
| PanningMethod | ECatPannerMethod | 声像算法：EqualPower（等功率）或 Linear（线性） |

### 使用示例（MetaSound 编辑器）

**场景：创建一个自适应通道格式的音频输出图**

1. 在 MetaSound 编辑器中创建新图
2. 添加 **CatMixer** 节点，设置 `FormatChoosingMethod` 为 `MetasoundOutput`（自动匹配输出设备格式）
3. 连接多个不同格式的音频输入到 CatMixer 的输入端
4. 如需最终转换，在 CatMixer 输出后连接 **CatCasting** 节点，指定目标格式

**场景：立体声声像控制**

1. 添加 **CatPanner** 节点
2. 设置 `PanToType` 为 `Cat:Stereo2Dot0`
3. 设置 `PanningMethod` 为 `EqualPower`
4. 连接 CAT 音频输入和方位角控制信号

## C++ 用法

### 头文件引入

```cpp
// CAT 核心类型
#include "MetasoundFormatAgnosticType.h"

// CatCasting 节点
#include "MetasoundCatCastingNode.h"

// CatPanner 节点
#include "MetasoundCatPannerNode.h"

// 示例节点配置
#include "MetasoundExampleNodeConfiguration.h"
```

### 基本用法

**使用方位角工具函数**（来自 `MetasoundCatPannerNode.h`）：

```cpp
#include "MetasoundCatPannerNode.h"

// 将归一化方位角（0.0-1.0）转换为角度（0-360）
float NormalizedAzimuth = 0.25f;  // 表示 90° 方向
float Degrees = Metasound::NormalizedAzimuthToDegrees(NormalizedAzimuth);
// Degrees = 90.0f
```

**自定义节点配置结构**（参考 `FMetaSoundExperimentalExampleNodeConfiguration`）：

```cpp
// 来源: Public/MetasoundExampleNodeConfiguration.h
// 自定义配置需要继承 FMetaSoundFrontendNodeConfiguration
struct FMyCustomNodeConfiguration : public FMetaSoundFrontendNodeConfiguration
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = General)
    FString MySetting;

    // 重写此方法以动态生成节点接口
    virtual TInstancedStruct<FMetasoundFrontendClassInterface> 
        OverrideDefaultInterface(const FMetasoundFrontendClass& InNodeClass) const override;

    // 重写此方法以传递运行时数据到 Operator
    virtual TSharedPtr<const Metasound::IOperatorData> 
        GetOperatorData() const override;
};
```

### 进阶用法

**创建自定义 Operator 并使用 TNodeFacade**（参考 `FCatCastingOperator`）：

```cpp
// 来源: Private/MetasoundCatCastingNode.h
namespace Metasound
{
    // 自定义 Operator 需要继承 TExecutableOperator
    class FMyOperator final : public TExecutableOperator<FMyOperator>
    {
    public:
        FMyOperator(const FBuildOperatorParams& InParams, /* 其他参数 */);
        
        // 定义节点接口（输入/输出端口）
        static FVertexInterface GetInterface(/* 参数 */);
        
        // 工厂方法，由框架调用以创建 Operator 实例
        static TUniquePtr<IOperator> CreateOperator(
            const FBuildOperatorParams& InParams, 
            FBuildResults& OutResults
        );

        // 绑定输入数据引用
        virtual void BindInputs(FInputVertexInterfaceData& InOutVertexData) override;
        
        // 绑定输出数据引用
        virtual void BindOutputs(FOutputVertexInterfaceData& InOutVertexData) override;

        // 重置状态
        void Reset(const FResetParams& InParams);

        // 每帧执行的核心逻辑
        void Execute();
    
        // 节点元数据
        static FNodeClassMetadata GetNodeInfo();
    };

    // 使用 TNodeFacade 将 Operator 包装为可注册的节点类
    using FMyNode = TNodeFacade<FMyOperator>;
}
```

**使用 TOperatorData 传递配置到 Operator**（参考 `FWidgetExampleOperatorData`）：

```cpp
// 来源: Public/MetasoundExampleNodeConfiguration.h
namespace Metasound::Experimental
{
    // 自定义 OperatorData 用于从配置传递数据到 Operator
    class FMyOperatorData : public TOperatorData<FMyOperatorData>
    {
    public:
        static const FLazyName OperatorDataTypeName;

        FMyOperatorData(const float& InFloat)
            : MyFloat(InFloat)
        {
        }

        float MyFloat;
    };
}
```

## Demo 示例

**最小 CAT 方位角工具使用示例**：

```cpp
// MyCatHelper.h
#pragma once

#include "CoreMinimal.h"
#include "MetasoundCatPannerNode.h"

class FMyCatHelper
{
public:
    // 将归一化方位角列表转换为角度
    static TArray<float> ConvertNormalizedAzimuths(const TArray<float>& InNormalizedAzimuths)
    {
        TArray<float> Results;
        Results.Reserve(InNormalizedAzimuths.Num());
        for (float NormAz : InNormalizedAzimuths)
        {
            Results.Add(Metasound::NormalizedAzimuthToDegrees(NormAz));
        }
        return Results;
    }
};
```

```cpp
// MyCatHelper.cpp
#include "MyCatHelper.h"

// 使用示例：
// TArray<float> Azimuths = { 0.0f, 0.25f, 0.5f, 0.75f };
// TArray<float> Degrees = FMyCatHelper::ConvertNormalizedAzimuths(Azimuths);
// 结果: { 0.0f, 90.0f, 180.0f, 270.0f }
```

## 模块依赖

本插件的 Build.cs 仅声明了 `CoreUObject` 依赖，但作为 MetaSound 的实验性扩展，实际使用时需要：

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心框架（插件级硬依赖） |
| `MetasoundFrontend` | MetaSound 前端节点配置和接口定义 |
| `AudioMixer` | 底层音频混合器，CAT 格式转换依赖其通道映射能力 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加 CAT 波形节点支持 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 修复 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 添加 CAT 乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 添加 CAT 梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261' | 从待提交变更集中恢复 |

### 维护评价

- **活跃程度**：🟢 **高度活跃** — 创建不到一个月，已有密集的功能提交
- **开发方向**：正在快速扩展 CAT 节点库（Wave、Multiply、Ladder Filter 等新节点）
- **稳定性**：⚠️ **不稳定** — 标记为实验性（IsExperimentalVersion=true），默认不启用，API 随时可能变化
- **来源**：从内部 NotForLicensees 目录迁出（CL 41822709），属于 Epic 内部开发中的前沿功能
- **依赖风险**：底层 FSoundWaveData API 已有废弃标记，合并冲突说明该插件与引擎其他部分的改动频繁交叉

**建议**：仅用于学习 MetaSound 节点扩展开发的模式和了解未来方向，**不建议用于生产项目**。CAT 框架设计理念先进，但 API 尚未稳定，等待其合并到主 MetaSound 插件后再正式采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [MetaSound 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)