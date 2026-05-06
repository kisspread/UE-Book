# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | MetaSound 实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、示例蓝图、节点配置） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Runtime → Editor 类型) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental) | |

---

## 用途

MetaSound 是 UE5 中用于程序化音频生成的高性能节点图系统。`Metasounds Experimental` 插件为该体系提供**实验性新功能**的孵化环境——这些功能尚未达到正式版质量标准，但可供开发者在实际项目中提前试用和反馈。

通过该插件，Epic 可以快速迭代新节点、新的输入/输出类型、编辑器定制化功能（如自定义 widget、映射函数可视化编辑），而不会影响核心 MetaSound 插件的稳定性。

目前包含的实验性功能示例：
- **Fade Node**：音频淡入淡出新节点
- **编辑器细节定制化**：提供 `FExampleWidgetNodeConfigurationCustomization` 和 `FMappingFunctionNodeConfigurationCustomization` 用于自定义节点配置界面
- **映射函数编辑器**：允许在 MetaSound 节点内直接编辑曲线（Mapping Function），并支持包裹模式（Wrap Inputs）

---

## 使用场景

- 你正在开发自定义 MetaSound 节点，需要测试新的输入/输出类型或特殊界面 → 利用提供的编辑器定制化基类快速实现
- 你希望使用 MetaSound 实现动态音频淡化效果（如淡入、淡出、交叉淡变） → 利用 `Fade Node`（内部实验节点）
- 你需要为 MetaSound 节点添加类似“映射曲线”的配置参数，并希望提供可视化曲线编辑 → 复用 `FMappingFunctionNodeConfigurationCustomization`

---

## 蓝图用法

由于该插件主要用于提供**新的 MetaSound 运行时节点**和**编辑器定制**，大部分功能不直接暴露为蓝图可调用的函数。不过，实验性节点（如 Fade Node）在添加后可以在 MetaSound 图中使用，而 MetaSound 图本身可在蓝图或 C++ 中调用。

若你需要在蓝图中使用实验性 MetaSound 节点，请确保：
1. 启用该插件（`Plugins → Audio → Metasounds Experimental`）
2. 在 MetaSound 编辑器中搜索“Fade”等关键词
3. 将节点拖入图并连接 Audio 输入/输出

无独立蓝图函数。

---

## C++ 用法

### 头文件引入

```cpp
// 使用编辑器定制化时
#include "MetasoundExampleNodeDetailsCustomization.h"
#include "MetasoundMappingFunctionDetailsCustomization.h"

// 使用实验性运行时节点（如 Fade Node）
#include "MetasoundExperimentalRuntimeModule.h"
```

### 基本用法 – 自定义节点配置 Widget

```cpp
// 在 MetaSound 节点类的自定义细节面板中注册
// 继承 FMetaSoundNodeConfigurationDataDetails 并重写 OnChildRowAdded
class FMyCustomization : public Metasound::Editor::FMetaSoundNodeConfigurationDataDetails
{
public:
    FMyCustomization(TSharedPtr<IPropertyHandle> InStructProperty, TWeakObjectPtr<UMetasoundEditorGraphNode> InNode)
        : FMetaSoundNodeConfigurationDataDetails(InStructProperty, InNode)
    {}

    virtual void OnChildRowAdded(IDetailPropertyRow& ChildRow) override
    {
        // 可以修改 ChildRow 的外观或添加自定义控件
        // 例如添加 float 属性的滑块范围限制
        if (MyFloatPropertyHandle.IsValid())
        {
            ChildRow.CustomWidget()
                .NameContent()
                [
                    ChildRow.GetPropertyHandle()->CreatePropertyNameWidget()
                ]
                .ValueContent()
                [
                    SNew(SSpinBox<float>)
                        .Value(this, &FMyCustomization::GetFloatValue)
                        .OnValueChanged(this, &FMyCustomization::SetFloatValue)
                ];
        }
    }

private:
    float GetFloatValue() const { return 0.5f; }
    void SetFloatValue(float NewValue) {}
};
```

**来源**: `Source/MetasoundExperimentalEditor/Private/MetasoundExampleNodeDetailsCustomization.h`

### 进阶用法 – 映射函数曲线编辑

`FMappingFunctionNodeConfigurationCustomization` 展示了如何在 MetaSound 节点属性面板中嵌入一个曲线编辑器，用于编辑 `FRuntimeFloatCurve` 数据。

```cpp
// 在 MetaSound 节点注册时，为特定结构体指定该定制类
// 详见 MetaSound 编辑器模块的注册代码

// 使用方式同基本用法，但重写 OnChildRowAdded 后会自动处理曲线属性
void FMappingFunctionNodeConfigurationCustomization::OnChildRowAdded(IDetailPropertyRow& ChildRow)
{
    // 获取 CurvePropertyHandle 和 bWrapInputsPropertyHandle
    // 创建 SCurveEditor 并嵌入到面板
    // 设置 FCurveOwnerInterface 回调以同步数据
}
```

**来源**: `Source/MetasoundExperimentalEditor/Private/MetasoundMappingFunctionDetailsCustomization.h`

---

## Demo 示例

以下是一个最小 C++ 示例，展示如何在插件模块启动时注册自定义节点配置定制类。

```cpp
// MetasoundExperimentalEditorModule.h
#pragma once
#include "Modules/ModuleInterface.h"

class FMetasoundExperimentalEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MetasoundExperimentalEditorModule.cpp
#include "MetasoundExperimentalEditorModule.h"
#include "MetasoundNodeConfigurationCustomization.h"
#include "MetasoundExampleNodeDetailsCustomization.h"
#include "MetasoundMappingFunctionDetailsCustomization.h"
#include "MetasoundEditorGraphNode.h"

void FMetasoundExperimentalEditorModule::StartupModule()
{
    // 注册 Example Widget 定制化（假设结构体类型名）
    Metasound::Editor::FMetaSoundNodeConfigurationDataDetails::Register(
        TEXT("ExampleWidgetConfig"),
        [](TSharedPtr<IPropertyHandle> StructProperty, TWeakObjectPtr<UMetasoundEditorGraphNode> Node)
        {
            return MakeShared<FExampleWidgetNodeConfigurationCustomization>(StructProperty, Node);
        }
    );

    // 注册 Mapping Function 曲线编辑器
    Metasound::Editor::FMetaSoundNodeConfigurationDataDetails::Register(
        TEXT("MappingFunctionConfig"),
        [](TSharedPtr<IPropertyHandle> StructProperty, TWeakObjectPtr<UMetasoundEditorGraphNode> Node)
        {
            return MakeShared<FMappingFunctionNodeConfigurationCustomization>(StructProperty, Node);
        }
    );
}

void FMetasoundExperimentalEditorModule::ShutdownModule() {}

IMPLEMENT_MODULE(FMetasoundExperimentalEditorModule, MetasoundExperimentalEditor);
```

> **注意**：以上代码需要根据实际结构体名称调整。`Register` 方法原型依赖于 MetaSound 编辑器内部 API，需包含相应头文件。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | 核心 MetaSound 运行时和编辑器（必需） |
| `AudioExperimentalRuntime` | 音频实验运行时（该插件内部模块） |
| `MetasoundExperimentalRuntime` | 实验性运行时节点（如 Fade Node） |
| `MetasoundExperimentalEngineRuntime` | 引擎集成实验 |
| `MetasoundExperimentalEditor` | 编辑器定制化模块 |

构建时，你的模块只需依赖 `Metasound` 即可使用其实验性节点（运行时），若需编辑器定制，则需额外依赖 `MetasoundExperimentalEditor`。

---

## 维护状态

### 近期更新

- 2025-09-30 `3a283b32` — [MetaSound Experimental] Fade Node 单元测试修复
- 2025-08-21 `51079168` — 改进 MetaSound 节点注册与模块关联
- 2025-08-15 `38229d1b` — MetaSound LOCTEXT 修正
- 2025-08-05 `da28318e` — [Metasound Experimental] 处理微小优化反馈
- 2025-08-05 `4c1309f1` — [Metasound Experimental] 添加 Fade Node

### 维护评价

- **创建时间**：2025-08-05（约 2 个月）
- **更新频率**：较高，每月有功能性和修复性提交
- **活跃度**：**活跃维护中**。当前为实验性插件，Epic 持续添加新功能并修复问题
- **已知限制**：
  - 属性表结构尚未稳定，可能随版本变更
  - 部分 API（如 `Register`）未公开文档，需阅读 MetaSound 核心源码
  - 编辑器定制化依赖 MetaSound 编辑器内部类，可能因版本更新而失效
- **推荐使用**：适合对 MetaSound 有深入需求的开发者，提前试用新特性。**不建议在生产项目**中依赖此插件，因其 API 可能随时变化。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档 (MetaSound 基础)](https://docs.unrealengine.com/5.7/en-US/metasound-in-unreal-engine/)
- [测试用例 (Fade Node 单元测试)] `Engine/Plugins/Experimental/MetasoundExperimental/Source/MetasoundExperimentalRuntime/Private/Tests/`(需克隆 UE5 源码查看)