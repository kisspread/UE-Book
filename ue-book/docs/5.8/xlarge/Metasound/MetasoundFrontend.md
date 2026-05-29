# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元声音 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetasoundFrontend` (Runtime), `MetasoundEngine` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime), `MetasoundEditor` (Runtime), `MetasoundEngineTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-23 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是 Unreal Engine 5 的核心音频系统，用于构建**基于节点图的音频 DSP（数字信号处理）流水线**。它解决的核心问题是：让音频设计师能在不编写 C++ 代码的情况下，通过可视化节点图实现复杂的音频生成与处理逻辑。

MetaSound 的核心架构分为三层：
- **Frontend 层**（本文档重点）：负责文档模型、节点注册、数据类型注册、搜索引擎、资产管理和序列化
- **GraphCore 层**：负责运行时图的构建与执行调度
- **Engine 层**：负责 MetaSound 资产（UObject）与音频引擎的集成

Frontend 模块是整个 MetaSound 系统的**数据基础层**，它定义了：
- 节点图的文档结构（`FMetasoundFrontendDocument`）
- 节点注册表（`INodeClassRegistry`）和数据类型注册表（`IDataTypeRegistry`）
- 资产管理系统（`IMetaSoundAssetManager`）
- 文档构建器（`FMetaSoundFrontendDocumentBuilder`）—— 用于程序化创建和修改 MetaSound
- 搜索引擎（`ISearchEngine`）—— 用于按名称/版本查询已注册的节点类
- 接口注册（`IInterfaceRegistry`）—— 管理 MetaSound 接口（如 SourceInterface、ParameterInterface）

## 使用场景

- 你需要实现复杂的音频效果链（如多段均衡器 + 延迟 + 混响）且需要实时参数控制 → 用 MetaSound 构建 DSP 图
- 你需要程序化生成音频图（运行时动态创建节点和连接） → 用 `FMetaSoundFrontendDocumentBuilder`
- 你需要注册自定义音频处理节点 → 用 `METASOUND_REGISTER_NODE` 宏和 `Frontend::RegisterNode<T>()`
- 你需要定义自定义音频数据类型 → 用 `METASOUND_REGISTER_METASOUND_DATATYPE` 宏
- 你需要在蓝图中设置 MetaSound 参数 → 用 `UMetasoundParameterPack`
- 你需要查询已注册的所有 MetaSound 节点类型 → 用 `ISearchEngine`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Metasound Parameter Pack` | 创建参数包实例 | `UMetasoundParameterPack` |
| `Set Bool` | 设置布尔参数 | `UMetasoundParameterPack` |
| `Set Int` | 设置整数参数 | `UMetasoundParameterPack` |
| `Set Float` | 设置浮点参数 | `UMetasoundParameterPack` |
| `Set String` | 设置字符串参数 | `UMetasoundParameterPack` |
| `Set Trigger` | 触发触发器参数 | `UMetasoundParameterPack` |
| `Get Bool` | 读取布尔参数 | `UMetasoundParameterPack` |
| `Get Int` | 读取整数参数 | `UMetasoundParameterPack` |
| `Get Float` | 读取浮点参数 | `UMetasoundParameterPack` |
| `Get String` | 读取字符串参数 | `UMetasoundParameterPack` |
| `Get Trigger` | 读取触发器参数 | `UMetasoundParameterPack` |
| `Has Bool` | 检查布尔参数是否存在 | `UMetasoundParameterPack` |
| `Has Float` | 检查浮点参数是否存在 | `UMetasoundParameterPack` |

### 使用示例

**设置 MetaSound 参数**：
1. 调用 `Make Metasound Parameter Pack` 创建一个 `UMetasoundParameterPack` 对象
2. 调用 `Set Float` 节点，传入参数名（如 `"Volume"`）和值
3. 将参数包传递给 MetaSound 组件的参数设置接口

**读取 MetaSound 参数**：
1. 从已有的参数包调用 `Get Float`，传入参数名
2. 蓝图执行引脚输出 `Succeeded` 或 `Failed`，结果引脚输出实际值

## C++ 用法

### 头文件引入

```cpp
#include "MetasoundFrontendDocument.h"
#include "MetasoundFrontendDocumentBuilder.h"
#include "MetasoundFrontendNodeClassRegistry.h"
#include "MetasoundFrontendDataTypeRegistry.h"
#include "MetasoundNodeRegistrationMacro.h"
#include "MetasoundFrontendModuleRegistrationMacros.h"
```

### 基本用法：注册自定义 MetaSound 节点

以下示例展示如何注册一个简单的 MetaSound 运算节点。来源：`MetasoundNodeRegistrationMacro.h` + `MetasoundArrayNodes.h` 的模式。

```cpp
// MyMetaSoundNode.h
#pragma once
#include "MetasoundOperatorInterface.h"
#include "MetasoundNode.h"
#include "MetasoundParam.h"

namespace Metasound
{
    // 定义输入/输出引脚
    namespace MyNodeVertexNames
    {
        METASOUND_PARAM(InputA, "A", "Input A")
        METASOUND_PARAM(InputB, "B", "Input B")
        METASOUND_PARAM(OutputResult, "Result", "Addition result")
    }

    // 运算器：在每个音频块执行实际计算
    class FMyAddOperator : public TExecutableOperator<FMyAddOperator>
    {
    public:
        FMyAddOperator(
            const FBuildOperatorParams& InParams,
            TDataReadReference<float> InA,
            TDataReadReference<float> InB)
            : A(InA)
            , B(InB)
            , Result(TDataWriteReference<float>::CreateNew(InParams.OperatorSettings))
        {
        }

        static TUniquePtr<IOperator> CreateOperator(
            const FBuildOperatorParams& InParams,
            FBuildResults& OutResults)
        {
            using namespace MyNodeVertexNames;
            const FInputVertexInterfaceData& InputData = InParams.InputData;
            auto A = InputData.GetOrCreateDefaultDataReadReference<float>(
                METASOUND_GET_PARAM_NAME(InputA), InParams.OperatorSettings);
            auto B = InputData.GetOrCreateDefaultDataReadReference<float>(
                METASOUND_GET_PARAM_NAME(InputB), InParams.OperatorSettings);
            return MakeUnique<FMyAddOperator>(InParams, A, B);
        }

        static const FNodeClassMetadata& GetNodeInfo()
        {
            auto Init = []() -> FNodeClassMetadata
            {
                FNodeClassMetadata Info;
                Info.ClassName = { "My", "Add", "" };
                Info.MajorVersion = 1;
                Info.MinorVersion = 0;
                Info.DisplayName = METASOUND_LOCTEXT("MyAddNode_DisplayName", "Add (Float)");
                Info.Description = METASOUND_LOCTEXT("MyAddNode_Desc", "Adds two floats together");
                Info.Author = TEXT("Me");
                Info.PromptIfMissing = PluginNodeMissingPrompt;
                Info.DefaultInterface = DeclareVertexInterface();
                Info.CategoryHierarchy = { METASOUND_LOCTEXT("MyCategory", "My Nodes") };
                return Info;
            };
            static const FNodeClassMetadata Info = Init();
            return Info;
        }

        static FVertexInterface DeclareVertexInterface()
        {
            using namespace MyNodeVertexNames;
            return FVertexInterface(
                FInputVertexInterface(
                    TInputDataVertex<float>(METASOUND_GET_PARAM_NAME(InputA)),
                    TInputDataVertex<float>(METASOUND_GET_PARAM_NAME(InputB))
                ),
                FOutputVertexInterface(
                    TOutputDataVertex<float>(METASOUND_GET_PARAM_NAME(OutputResult))
                )
            );
        }

        void BindInputs(FInputVertexInterfaceData& InData) override
        {
            using namespace MyNodeVertexNames;
            InData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputA), A);
            InData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputB), B);
        }

        void BindOutputs(FOutputVertexInterfaceData& InData) override
        {
            using namespace MyNodeVertexNames;
            InData.BindReadVertex(METASOUND_GET_PARAM_NAME(OutputResult), Result);
        }

        void Execute()
        {
            *Result = *A + *B;
        }

        void Reset(const IOperator::FResetParams& InParams)
        {
            *Result = 0.0f;
        }

    private:
        TDataReadReference<float> A;
        TDataReadReference<float> B;
        TDataWriteReference<float> Result;
    };
}
```

### 进阶用法：程序化构建 MetaSound 文档

以下展示使用 `FMetaSoundFrontendDocumentBuilder` 在运行时动态构建 MetaSound 图。来源：`MetasoundFrontendDocumentBuilder.h`。

```cpp
#include "MetasoundFrontendDocumentBuilder.h"
#include "MetasoundFrontendDocument.h"

// 假设你有一个实现了 IMetaSoundDocumentInterface 的 UMetaSound 子类
void BuildMetaSoundAtRuntime(UMyMetaSoundAsset* InAsset)
{
    // 获取文档构建器（会缓存加速后续操作）
    FMetaSoundFrontendDocumentBuilder& Builder =
        Metasound::Frontend::IDocumentBuilderRegistry::GetChecked()
            .FindOrBeginBuilding(InAsset);

    // 设置构建目标页面
    Builder.SetBuildPageID(Metasound::Frontend::DefaultPageID);

    // 添加音频输入
    FMetasoundFrontendClassInput AudioInput;
    AudioInput.Name = TEXT("AudioIn");
    AudioInput.TypeName = TEXT("Audio");
    AudioInput.AccessType = EMetasoundFrontendVertexAccessType::Value;
    Builder.AddGraphInput(AudioInput);

    // 添加音频输出
    FMetasoundFrontendClassOutput AudioOutput;
    AudioOutput.Name = TEXT("AudioOut");
    AudioOutput.TypeName = TEXT("Audio");
    AudioOutput.AccessType = EMetasoundFrontendVertexAccessType::Value;
    Builder.AddGraphOutput(AudioOutput);

    // 添加一个增益节点（假设已注册）
    FMetasoundFrontendClassName GainClassName;
    GainClassName.Namespace = TEXT("UE");
    GainClassName.Name = TEXT("Gain");
    GainClassName.Variant = TEXT("");
    const FMetasoundFrontendNode* GainNode = Builder.AddNodeByClassName(GainClassName);

    // 添加边：Audio Input → Gain Input
    FMetasoundFrontendEdge InputEdge;
    InputEdge.FromNodeID = /* 输入节点的 ID */;
    InputEdge.FromVertexID = /* 输入引脚 ID */;
    InputEdge.ToNodeID = GainNode->GetID();
    InputEdge.ToVertexID = /* Gain 输入引脚 ID */;
    Builder.AddEdge(MoveTemp(InputEdge));

    // 添加边：Gain Output → Audio Output
    FMetasoundFrontendEdge OutputEdge;
    OutputEdge.FromNodeID = GainNode->GetID();
    OutputEdge.FromVertexID = /* Gain 输出引脚 ID */;
    OutputEdge.ToNodeID = /* 输出节点的 ID */;
    OutputEdge.ToVertexID = /* 输出引脚 ID */;
    Builder.AddEdge(MoveTemp(OutputEdge));

    // 完成构建，会注册到前端节点类注册表
    Builder.FinishBuilding();
}
```

### 进阶用法：注册自定义数据类型

来源：`MetasoundDataTypeRegistrationMacro.h`。

```cpp
// 在你的模块的 StartupModule 中
#include "MetasoundDataTypeRegistrationMacro.h"
#include "MetasoundFrontendModuleRegistrationMacros.h"

// 在 Build.cs 中定义：
// PrivateDefinitions.Add("METASOUND_PLUGIN=MyPlugin")
// PrivateDefinitions.Add("METASOUND_MODULE=MyModule")

// 在模块头文件中：
// METASOUND_DEFINE_MODULE_REGISTRATION_LIST

// 在模块 .cpp 中：
// METASOUND_IMPLEMENT_MODULE_REGISTRATION_LIST

void FMyModule::StartupModule()
{
    METASOUND_REGISTER_ITEMS_IN_MODULE
}

void FMyModule::ShutdownModule()
{
    METASOUND_UNREGISTER_ITEMS_IN_MODULE
}

// 注册自定义数据类型（通常在静态初始化中完成）
METASOUND_REGISTER_METASOUND_DATATYPE(FMyCustomType, "MyCustomType")
```

## Demo 示例

一个最小化的自定义 MetaSound 节点注册示例，包含完整的模块注册流程。

**MyMetaSoundNodes.h**
```cpp
#pragma once
#include "MetasoundNode.h"
#include "MetasoundOperatorInterface.h"
#include "MetasoundParam.h"

namespace Metasound
{
    namespace DoubleFloatVertexNames
    {
        METASOUND_PARAM(InputValue, "In", "Input float value")
        METASOUND_PARAM(OutputValue, "Out", "Doubled output")
    }

    class FDoubleFloatOperator : public TExecutableOperator<FDoubleFloatOperator>
    {
    public:
        FDoubleFloatOperator(
            const FBuildOperatorParams& InParams,
            TDataReadReference<float> InInput)
            : Input(InInput)
            , Output(TDataWriteReference<float>::CreateNew(InParams.OperatorSettings))
        {
        }

        static TUniquePtr<IOperator> CreateOperator(
            const FBuildOperatorParams& InParams,
            FBuildResults& OutResults)
        {
            using namespace DoubleFloatVertexNames;
            auto In = InParams.InputData.GetOrCreateDefaultDataReadReference<float>(
                METASOUND_GET_PARAM_NAME(InputValue), InParams.OperatorSettings);
            return MakeUnique<FDoubleFloatOperator>(InParams, In);
        }

        static const FNodeClassMetadata& GetNodeInfo()
        {
            static const FNodeClassMetadata Info = []()
            {
                FNodeClassMetadata Meta;
                Meta.ClassName = { "My", "DoubleFloat", "" };
                Meta.MajorVersion = 1;
                Meta.MinorVersion = 0;
                Meta.DisplayName = METASOUND_LOCTEXT("DoubleFloat_Disp", "Double Float");
                Meta.Description = METASOUND_LOCTEXT("DoubleFloat_Desc", "Doubles a float value");
                Meta.Author = TEXT("Example");
                Meta.PromptIfMissing = PluginNodeMissingPrompt;
                Meta.DefaultInterface = FVertexInterface(
                    FInputVertexInterface(
                        TInputDataVertex<float>(METASOUND_GET_PARAM_NAME(InputValue))
                    ),
                    FOutputVertexInterface(
                        TOutputDataVertex<float>(METASOUND_GET_PARAM_NAME(OutputValue))
                    )
                );
                Meta.CategoryHierarchy = { METASOUND_LOCTEXT("DemoCat", "Demo") };
                return Meta;
            }();
            return Info;
        }

        void BindInputs(FInputVertexInterfaceData& InData) override
        {
            InData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputValue), Input);
        }

        void BindOutputs(FOutputVertexInterfaceData& InData) override
        {
            InData.BindReadVertex(METASOUND_GET_PARAM_NAME(OutputValue), Output);
        }

        void Execute()
        {
            *Output = *Input * 2.0f;
        }

        void Reset(const IOperator::FResetParams&)
        {
            *Output = 0.0f;
        }

    private:
        TDataReadReference<float> Input;
        TDataWriteReference<float> Output;
    };
}
```

**MyMetaSoundModule.cpp**
```cpp
#include "Modules/ModuleManager.h"
#include "MetasoundFrontendModuleRegistrationMacros.h"
#include "MetasoundNodeRegistrationMacro.h"
#include "MyMetaSoundNodes.h"

// 在 Build.cs 中定义:
// PrivateDefinitions.Add("METASOUND_PLUGIN=MyPlugin")
// PrivateDefinitions.Add("METASOUND_MODULE=MyModule")

METASOUND_IMPLEMENT_MODULE_REGISTRATION_LIST

class FMyMetaSoundModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        using namespace Metasound;
        METASOUND_REGISTER_ITEMS_IN_MODULE

        // 注册自定义节点
        Frontend::RegisterNode<FDoubleFloatOperator>(Frontend::FModuleInfo{});
    }

    virtual void ShutdownModule() override
    {
        METASOUND_UNREGISTER_ITEMS_IN_MODULE
    }
};

IMPLEMENT_MODULE(FMyMetaSoundModule, MyModule)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

注：MetasoundFrontend 的 `Build.cs` 主要依赖 `Core`、`CoreUObject`、`Engine` 等标准模块。该模块刻意保持轻量，不依赖 UnrealEd，使其可在运行时和编辑器构建中使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复删除后重新添加 Page 图时触发的断言错误 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 防止对不可引用的父 MetaSound 创建预设时崩溃 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 在正式构建中保护目标 PageID 不被意外修改 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 清理之前进入 PIE 时死锁修复的代码 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 尝试性修复进入 PIE 编辑器时的冻结问题 |

### 维护评价

**活跃维护**。MetaSound 是 UE5 的核心音频系统，由 Epic Games 音频团队持续维护。从最近的提交记录来看，团队仍在积极修复 bug 和改进稳定性（Page 图管理、PIE 死锁、预设创建安全保护等）。

- **创建时间**：2020 年 5 月，约 6 年历史
- **更新频率**：持续有实质性更新，最近提交集中在 2026 年 5 月
- **维护状态**：**活跃维护中**，是 Epic 官方重点支持的音频系统
- **已知限制**：Send/Receive 节点已被标记为 Deprecated（`EnumAddFlags(Info.AccessFlags, ENodeClassAccessFlags::Deprecated)`），建议使用参数直接传递数据
- **推荐使用**：**强烈推荐**。MetaSound 是 UE5 中音频设计的首选方案，取代了 UE4 的 Sound Cue 系统。对于程序化音频需求，使用 `FMetaSoundFrontendDocumentBuilder` API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/Audio/MetaSounds/)（无 DocsURL，使用通用 MetaSound 文档页）