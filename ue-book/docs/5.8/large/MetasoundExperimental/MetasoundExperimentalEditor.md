# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 元声音实验版 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性音频资产和编辑器扩展） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

该插件是 UE5 高级音频系统 **Metasound** 的**实验性功能孵化器**。它存在的目的是在新特性（如新的音频节点类型、资产类型或编辑器功能）正式发布到 `Metasound` 主插件之前，提供一个隔离的测试和开发环境。

**核心价值**：
1.  **功能预览**：允许开发者提前使用尚在开发中、可能不稳定的 Metasound 新功能。
2.  **安全隔离**：将实验代码与稳定版的 Metasound 插件分离，避免影响正式项目。
3.  **迭代开发**：Epic 可以在此插件内快速迭代新的音频处理概念，并收集早期用户反馈。

从源码看，它包含了如 **通道无关类型（CAT）波形**、**映射函数节点**、**颗粒合成节点**等实验性功能的运行时支持和编辑器定制。

## 使用场景

-   你是一名**音频程序员或技术音效设计师**，希望**提前尝试并反馈 Metasound 的新功能**（如新的滤波器、波形处理节点等）。
-   你正在开发一个**前沿的音频交互项目**，需要使用到尚未在正式版中提供的 Metasound 特性。
-   你是一名**引擎贡献者**，正在为 Metasound 开发新节点或资产类型，并需要在此插件内进行测试。

**重要提示**：此插件**默认不启用**，且其 API 和功能**可能在未来版本中更改、重构或移除**。不建议在面向正式发布的项目中依赖此插件内的功能。

## 蓝图用法

由于该插件主要是实验性运行时和编辑器扩展，并且核心 Metasound 功能通常通过编辑器中的 MetaSound 蓝图图来使用，其直接蓝图节点较少。提供的头文件主要面向 **C++ 编辑器扩展**。

### 核心资产类型（编辑器）

在启用插件后，你可能会在内容浏览器中看到新的资产类型：

| 资产类型 | 说明 |
|---|---|
| `CatSoundWaveContainer` | 一种实验性的容器资产，用于存储和引用 `FSoundWaveData`，可能与新的“通道无关类型（CAT）”系统相关。 |

## C++ 用法

此插件的功能主要通过 C++ 实现。使用者主要是引擎开发者和需要深度集成实验性音频功能的程序员。

### 头文件引入

由于是实验性插件，头文件路径可能随版本变化。以下为基于源码结构的示例：

```cpp
// 引入编辑器模块（用于资产定义或自定义节点UI）
#include "AssetDefinition_CatSoundWaveContainer.h"

// 注意：运行时模块（如 AudioExperimentalRuntime, MetasoundExperimentalRuntime）的头文件
// 通常用于实现实验性的音频节点或数据类型，但具体头文件名需查阅源码。
```

### 基本用法：定义新的实验性资产

以下示例展示了如何为一个新的实验性资产类型创建编辑器定义，参考了 `AssetDefinition_CatSoundWaveContainer.h` 的模式。

**来源文件**: `Private/AssetDefinitions/AssetDefinition_CatSoundWaveContainer.h`

```cpp
// MyExperimentalAssetDefinition.h
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyExperimentalAsset.h" // 你的实验性资产头文件

UCLASS(MinimalAPI)
class UAssetDefinition_MyExperimentalAsset : public UAssetDefinitionDefault
{
	GENERATED_BODY()

public:
	// 资产在内容浏览器中的显示名称
	virtual FText GetAssetDisplayName() const override
	{
		return NSLOCTEXT("AssetDefinition", "MyExperimentalAsset", "My Experimental Asset");
	}

	// 资产在内容浏览器中的图标颜色
	virtual FLinearColor GetAssetColor() const override
	{
		return FLinearColor::Red; // 使用醒目颜色标识实验性资产
	}

	// 指向此资产定义所关联的UObject类
	virtual TSoftClassPtr<UObject> GetAssetClass() const override
	{
		return UMyExperimentalAsset::StaticClass();
	}

	// 在内容浏览器的“新建资产”菜单中放置的分类路径
	virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
	{
		static const TArray<FAssetCategoryPath> Categories = { FAssetCategoryPath(NSLOCTEXT("AssetDefinition", "Experimental", "Experimental")) };
		return Categories;
	}

	// 禁用从此资产类型导入
	virtual bool CanImport() const override
	{
		return false;
	}
};
```

### 进阶用法：为实验性 MetaSound 节点定制编辑器 UI

此插件提供了自定义 MetaSound 节点详情面板的机制，参考了 `FMappingFunctionNodeConfigurationCustomization` 等类。

```cpp
// MyNodeConfigurationCustomization.h
#pragma once

#include "MetasoundNodeConfigurationCustomization.h" // 假设基类来自MetasoundEditor模块
#include "Styling/SlateTypes.h" // 用于 SCheckBox 等

class FMyNodeConfigurationCustomization : public Metasound::Editor::FMetaSoundNodeConfigurationCustomization
{
public:
    FMyNodeConfigurationCustomization(TSharedPtr<IPropertyHandle> InStructProperty, TWeakObjectPtr<UMetasoundEditorGraphNode> InNode);

    // 重写此函数以在节点的详情面板中添加自定义行
    virtual void OnChildRowAdded(IDetailPropertyRow& ChildRow) override;

private:
    // 响应属性变更的回调
    void OnMyToggleChanged(const FPropertyChangedEvent& InPropertyChangedEvent);

    TSharedPtr<IPropertyHandle> MyTogglePropertyHandle;
};
```

```cpp
// MyNodeConfigurationCustomization.cpp
#include "MyNodeConfigurationCustomization.h"
#include "DetailLayoutBuilder.h"
#include "DetailWidgetRow.h"
#include "Widgets/Input/SCheckBox.h"

FMyNodeConfigurationCustomization::FMyNodeConfigurationCustomization(TSharedPtr<IPropertyHandle> InStructProperty, TWeakObjectPtr<UMetasoundEditorGraphNode> InNode)
    : Metasound::Editor::FMetaSoundNodeConfigurationCustomization(InStructProperty, InNode)
{
    // 获取结构体中某个布尔属性的句柄
    MyTogglePropertyHandle = InStructProperty->GetChildHandle(GET_MEMBER_NAME_CHECKED(FMyNodeConfiguration, bMyToggle));
}

void FMyNodeConfigurationCustomization::OnChildRowAdded(IDetailPropertyRow& ChildRow)
{
    // 如果是我们关心的属性行，则替换其默认 widget
    if (ChildRow.GetPropertyHandle() == MyTogglePropertyHandle)
    {
        ChildRow.CustomWidget()
        .NameContent()
        [
            MyTogglePropertyHandle->CreatePropertyNameWidget()
        ]
        .ValueContent()
        .MinDesiredWidth(200)
        [
            SNew(SCheckBox)
            .IsChecked_Lambda([this]() -> ECheckBoxState
            {
                bool bValue;
                MyTogglePropertyHandle->GetValue(bValue);
                return bValue ? ECheckBoxState::Checked : ECheckBoxState::Unchecked;
            })
            .OnStateChanged_Lambda([this](ECheckBoxState NewState)
            {
                MyTogglePropertyHandle->SetValue(NewState == ECheckBoxState::Checked);
            })
        ];
    }
}
```

## Demo 示例

一个最小的演示，展示如何**手动启用该插件并创建一个实验性资产**。

1.  **启用插件**：
    -   打开编辑器 → 编辑(Edit) → 插件(Plugins)
    -   在搜索框中输入 “Metasounds Experimental”
    -   找到 “Metasounds Experimental” 插件，勾选 “Enabled”
    -   重启编辑器

2.  **创建资产**：
    -   在内容浏览器空白处右键
    -   选择 “新建资产” → “Audio” → “Experimental” → “Cat Sound Wave Container” (或类似名称)
    -   你将在内容浏览器中看到一个带有醒目颜色（如红色）图标的新资产。

## 模块依赖

要在你的 C++ 模块中使用此插件的实验性功能，你需要在 `.Build.cs` 文件中添加依赖。由于此插件是实验性的，依赖的具体模块名称可能需要根据你使用的具体功能调整。

| 模块 | 用途 |
|---|---|
| `MetasoundExperimentalRuntime` | 使用实验性的 Metasound 运行时功能（如 CAT 波形节点）。 |
| `AudioExperimentalRuntime` | 使用更底层的实验性音频运行时功能。 |
| `MetasoundExperimentalEditor` | 扩展实验性 Metasound 节点或资产的编辑器 UI（仅在编辑器模块中依赖）。 |

**重要**：这些模块本身依赖于核心 `Metasound` 插件，因此在你的 `.Build.cs` 中可能也需要添加对 `Metasound` 的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加实验性的 MetaSound 通道无关类型 (CAT) 波形。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 弃用修复的合并冲突。 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | [CAT] 乘法节点。 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | [CAT] 阶梯滤波器节点。 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': ... | 从待定更改列表中恢复… |

### 维护评价

-   **创建时间**：非常新（约 1 年），是为 UE5 现代化音频系统专门设立的实验场。
-   **活跃度**：**高度活跃**。最近更新（2026年5月）表明 Epic 正在积极开发和迭代新的 Metasound 功能（如 CAT 系统），并在此插件中进行集成。
-   **状态**：**实验性开发中**。功能和 API 不稳定，是实验性功能的试验田。
-   **建议**：**强烈推荐**给希望探索和反馈 Metasound 未来发展方向的开发者。**不推荐**用于需要稳定性的生产项目。使用时应做好功能可能随版本更新而大幅调整的心理准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档](https://docs.unrealengine.com/) (注意：实验性插件可能没有专门的官方文档，相关功能文档会随正式版本发布)