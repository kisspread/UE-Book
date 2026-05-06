# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | MetaSound 实验性插件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 节点定义和配置） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

该插件是 MetaSound 框架的实验性功能预览区，存放尚未成熟到进入主插件的新特性。根据提供的源文件，当前核心功能包括：

- **Fade 节点** (`MetasoundFadeNode`)：对音频信号施加淡入/淡出效果，输出可选择浮点控制值或音频缓冲。
- **Mapping 函数节点** (`MetasoundMappingFunctionNode`)：使用用户定义的曲线（`FRuntimeFloatCurve`）将输入值映射到输出值，可选地循环（wrap）超出范围的输入。

这些节点通过自定义节点配置（`FMetaSoundFrontendNodeConfiguration` 的子类）实现，允许在 MetaSound 图中动态生成接口并传递自定义操作数据（`IOperatorData`）。

## 使用场景

- **音频淡入淡出**：在你的 MetaSound 图中添加一个 Fade 节点，控制音量的平滑过渡，常用于过场动画、UI 音效或场景切换。
- **非线性映射**：使用 Mapping 函数节点将控制参数（如 MIDI CC、游戏变量）通过自定义曲线转换为另一范围的值，例如将输入速度映射为音量缩放曲线。
- **实验性功能验证**：作为 MetaSound 开发人员的测试床，用于评估新节点在真实项目中的表现，之后再考虑纳入正式插件。

## 蓝图用法

MetaSound 实验性节点并非作为常规蓝图函数或类暴露，而是通过 MetaSound 图的节点系统使用。在编辑器中，当节点被注册后，你可以在 MetaSound 图形编辑器中找到它们并连接。其配置属性（如输出类型、曲线数据）可在节点的细节面板中编辑。

没有 `BlueprintCallable` 函数可供调用。若需在蓝图中创建或操作这些节点，需要通过 `Metasound::Frontend` 命名空间的 C++ API 动态注册节点类。

## C++ 用法

### 头文件引入

```cpp
#include "MetasoundFadeNode.h"
#include "MetasoundMappingFunctionNode.h"
```

### 基本用法

以下示例展示如何创建 Fade 节点配置并注册到 MetaSound 类：

```cpp
// 创建 Fade 节点配置
FMetaSoundFadeNodeConfiguration FadeConfig;
FadeConfig.OutputType = EMetaSoundFadeOutputType::FloatType;

// 获取操作数据（可选）
TSharedPtr<const Metasound::IOperatorData> OpData = FadeConfig.GetOperatorData();

// 将配置应用于 MetaSound 类（需要前端文档 API）
// 通常通过重写 OverrideDefaultInterface 实现
```

Mapping 函数节点的类似用法：

```cpp
// 创建 Mapping 函数节点配置
FMetaSoundMappingFunctionNodeConfiguration MappingConfig;
MappingConfig.bWrapInputs = true;

// 设置映射曲线
FRichCurve* Curve = MappingConfig.MappingFunction.GetRichCurve();
Curve->AddKey(0.0f, 0.0f);
Curve->AddKey(1.0f, 1.0f);

TSharedPtr<const Metasound::IOperatorData> OpData = MappingConfig.GetOperatorData();
```

### 进阶用法

自定义 MetaSound 节点通常需要继承 `UObject` 并通过反射系统注册。实验性插件中的节点通过“节点配置”（`FMetaSoundFrontendNodeConfiguration` 子类）与前端系统交互。你可以实现自己的配置类，借助已有的 `FMappingFunctionNodeOperatorData` 模式创建自定义操作数据。

```cpp
// 自定义操作数据示例
class FMyCustomOperatorData : public Metasound::TOperatorData<FMyCustomOperatorData>
{
public:
    static const Metasound::FLazyName OperatorDataTypeName;
    // 自定义数据成员
};

// 在节点配置的 GetOperatorData() 中返回
TSharedPtr<const Metasound::IOperatorData> GetOperatorData() const override
{
    return MakeShared<FMyCustomOperatorData>(...);
}
```

## Demo 示例

由于缺少完整源码，以下是一个概念性示例，展示如何在 C++ 模块中注册 Fade 节点并使其在 MetaSound 编辑器中可用。

**MetaSoundFadeNodeRegistration.h**

```cpp
#pragma once
#include "MetasoundFadeNode.h"
#include "MetasoundFrontend.h"

class FMetasoundFadeNodeRegistration
{
public:
    static void RegisterNode()
    {
        // 创建节点配置（需 MetaSound 前端注册 API）
        TUniquePtr<FMetaSoundFadeNodeConfiguration> Config = MakeUnique<FMetaSoundFadeNodeConfiguration>();
        // 注册节点...
    }
};
```

**MetaSoundFadeNodeRegistration.cpp**

```cpp
#include "MetaSoundFadeNodeRegistration.h"

void FMetasoundFadeNodeRegistration::RegisterNode()
{
    // 实际注册逻辑依赖于 MetaSound 内部 API
    // 推荐参考 Metasound 源文件中的节点注册模式
}
```

> **注意**：当前插件仍在实验阶段，节点注册的具体 API 可能随引擎版本变化。请参照 `Engine/Plugins/Experimental/MetasoundExperimental/Source` 中的实际实现。

## 模块依赖

以下模块是使用本插件时需要在项目或插件中引用的依赖：

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 主插件，提供核心节点系统和前端文档 API |
| `MetasoundExperimentalRuntime` | 本插件的运行时模块，包含通用实验性功能 |
| `AudioExperimentalRuntime` | 本插件的音频实验运行时模块 |

**注意**：`MetasoundExperimentalEngineRuntime` 本身只依赖 `CoreUObject`（常见依赖已省略），但它依赖于上述其他模块的功能。在代码中引入头文件时，请确保 `MetasoundExperimentalRuntime` 和 `Metasound` 已添加到模块的 `PublicDependencyModuleNames` 中。

## 维护状态

### 近期更新

- 2025-09-30 — `3a283b32` [MetaSound Experimental] Fade Node unit test fix
- 2025-08-21 — `51079168` Improve metasound node registration association with modules
- 2025-08-15 — `38229d1b` Metasound LOCTEXT fixups
- 2025-08-05 — `da28318e` [Metasound Experimental] Addressed minor optimization feedback
- 2025-08-05 — `4c1309f1` [Metasound Experimental] - Added Fade Node

### 维护评价

该插件创建于2025年8月，属于全新实验性插件（约0年）。最近一次更新在2025年9月30日，仍在积极开发和修复中。当前版本包含两个实验性节点，功能有限但代码结构清晰。因其实验性质，API 可能在不通知的情况下变更，不建议用于生产环境。适合希望在 MetaSound 框架中体验前沿功能的音频工程师。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档](https://docs.unrealengine.com/5.7/ProgrammingAndScripting/Audio/MetaSound/)（MetaSound 通用文档，本插件暂无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental/Source/MetasoundExperimentalEngineRuntime/Private)（当前模块私有源码目录）