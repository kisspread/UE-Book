# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 元声音实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、节点资产） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

MetasoundExperimental 是 MetaSound 系统的**实验性功能孵化场**，用于在正式发布前测试和迭代新的音频节点、资产类型和编辑器功能。该插件不面向生产环境，而是为 Epic 内部开发者提供一个隔离空间，将尚处于开发阶段的 MetaSound 新特性提前暴露给技术用户进行评估。

从源码分析来看，当前主要包含以下实验性功能：

1. **CAT（Channel Agnostic Types）Wave**：通道无关类型的音频波形容器，允许以与通道数无关的方式处理音频数据
2. **映射函数节点**（Mapping Function Node）：支持富曲线编辑的节点配置，可在编辑器中可视化调整音频映射曲线
3. **颗粒合成节点**（Granular Node）：支持包络类型选择的颗粒合成器节点
4. **示例 Widget 节点**：用于演示如何创建带自定义编辑器界面的 MetaSound 节点

该插件需要手动启用（`EnabledByDefault: false`），且标记为实验性（`IsExperimentalVersion: true`），意味着 API 随时可能发生变化。

## 使用场景

- 你想在 MetaSound 图中使用**通道无关类型**的音频处理流程 → 启用此插件获取 CAT Wave 资产类型
- 你需要在 MetaSound 中使用**映射函数节点**并通过曲线编辑器调整输入输出映射 → 使用映射函数节点及其编辑器自定义
- 你在研究**颗粒合成**音频效果并希望在 MetaSound 图中使用颗粒合成节点 → 启用此插件
- 你是 MetaSound 节点开发者，想参考**自定义节点编辑器界面**的实现方式 → 查看示例 Widget 节点代码
- 你想提前体验 MetaSound 即将推出的新特性 → 等待此插件中的功能毕业到正式 MetaSound 插件

## 蓝图用法

该插件主要提供 MetaSound 节点和资产定义，不直接暴露传统的蓝图可调用函数。核心功能通过 MetaSound 编辑器图中的节点操作体现。

### 资产类型

| 资产 | 说明 |
|---|---|
| CAT Sound Wave Container | 通道无关类型的音频波形容器，用于在 CAT 管线中封装音频数据 |

### 节点类型（MetaSound 图中可用）

| 节点 | 说明 |
|---|---|
| Mapping Function | 支持富曲线编辑的映射函数节点，可将输入值通过自定义曲线映射到输出值 |
| Granular Synthesis | 颗粒合成节点，支持可配置的包络类型 |
| Multiply (CAT) | CAT 通道无关乘法节点 |
| Ladder Filter (CAT) | CAT 通道无关梯形滤波器节点 |

### 使用示例（编辑器操作）

1. **启用插件**：编辑 → 插件 → 搜索 "Metasound Experimental" → 启用 → 重启编辑器
2. **创建 CAT Sound Wave Container**：右键 Content Browser → Audio → Cat Sound Wave Container
3. **在 MetaSound 图中使用节点**：在 MetaSound 编辑器中右键 → 搜索 "Mapping Function" 或 "Granular" 等实验性节点
4. **编辑映射函数曲线**：选中 Mapping Function 节点 → 在 Details 面板中通过曲线编辑器调整映射曲线

## C++ 用法

该插件的 C++ 层主要面向节点开发者，提供节点配置自定义和资产定义扩展框架。

### 头文件引入

```cpp
// 编辑器自定义
#include "MetasoundMappingFunctionDetailsCustomization.h"
#include "MetasoundGranularNodeDetailsCustomization.h"

// 资产定义
#include "AssetDefinitions/AssetDefinition_CatSoundWaveContainer.h"
```

### 基本用法：自定义节点配置面板

从 `MetasoundExampleNodeDetailsCustomization.h` 提取的模式，展示如何为 MetaSound 节点创建自定义 Details 面板：

```cpp
// 继承 FMetaSoundNodeConfigurationCustomization 来自定义节点的属性面板
// 来源: Source/MetasoundExperimentalEditor/Private/MetasoundExampleNodeDetailsCustomization.h
class FMyNodeConfigurationCustomization 
    : public Metasound::Editor::FMetaSoundNodeConfigurationCustomization
{
public:
    FMyNodeConfigurationCustomization(
        TSharedPtr<IPropertyHandle> InStructProperty,
        TWeakObjectPtr<UMetasoundEditorGraphNode> InNode);

    // 自定义子属性行的显示方式
    virtual void OnChildRowAdded(IDetailPropertyRow& ChildRow) override;

private:
    void OnChildPropertyChanged(const FPropertyChangedEvent& InPropertyChangedEvent);
    
    FString StructPropertyPath;
    TSharedPtr<IPropertyHandle> MyFloatPropertyHandle;
};
```

### 进阶用法：带曲线编辑器的节点配置

从 `MetasoundMappingFunctionDetailsCustomization.h` 提取，展示如何集成 `FCurveOwnerInterface` 实现可视化曲线编辑：

```cpp
// 来源: Source/MetasoundExperimentalEditor/Private/MetasoundMappingFunctionDetailsCustomization.h
class FMappingFunctionNodeConfigurationCustomization 
    : public Metasound::Editor::FMetaSoundNodeConfigurationCustomization
    , public FCurveOwnerInterface
{
public:
    FMappingFunctionNodeConfigurationCustomization(
        TSharedPtr<IPropertyHandle> InStructProperty,
        TWeakObjectPtr<UMetasoundEditorGraphNode> InNode);

    virtual void OnChildRowAdded(IDetailPropertyRow& ChildRow) override;

    // FCurveOwnerInterface - 提供曲线数据给 SCurveEditor
    virtual TArray<FRichCurveEditInfo> GetCurves() override;
    virtual bool HasRichCurves() const override { return true; }
    virtual bool IsLinearColorCurve() const override { return false; }
    virtual void OnCurveChanged(const TArray<FRichCurveEditInfo>& ChangedCurveEditInfos) override;
    virtual TArray<const UObject*> GetOwners() const override;

private:
    void UpdateMappingFunctionData();

    FRuntimeFloatCurve* RuntimeCurve = nullptr;
    TSharedPtr<SCurveEditor> CurveEditorWidget;
    TSharedPtr<IPropertyHandle> CurvePropertyHandle;
    TSharedPtr<IPropertyHandle> bWrapInputsPropertyHandle;
};
```

### 资产定义扩展

从 `AssetDefinition_CatSoundWaveContainer.h` 提取，展示如何定义新资产类型：

```cpp
// 来源: Source/MetasoundExperimentalEditor/Private/AssetDefinitions/AssetDefinition_CatSoundWaveContainer.h
UCLASS(MinimalAPI)
class UAssetDefinition_CatSoundWaveContainer : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override;
    virtual FLinearColor GetAssetColor() const override;
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    virtual bool CanImport() const override;
};

// 右键菜单扩展
class FCatSoundWaveContainerExtension
{
public:
    static void RegisterMenus();
    static void Execute(const FToolMenuContext& MenuContext);
};
```

## Demo 示例

以下展示如何在你的编辑器模块中注册一个自定义的 MetaSound 节点配置面板：

```cpp
// MyMetaSoundNodeCustomization.h
#pragma once

#include "MetasoundEditorModule.h"
#include "IDetailPropertyRow.h"

class FMyGranularNodeCustomization 
    : public Metasound::Editor::FMetaSoundNodeConfigurationCustomization
{
public:
    FMyGranularNodeCustomization(
        TSharedPtr<IPropertyHandle> InStructProperty,
        TWeakObjectPtr<UMetasoundEditorGraphNode> InNode);

    virtual void OnChildRowAdded(IDetailPropertyRow& ChildRow) override;

private:
    void OnEnvelopeTypeChanged(const FPropertyChangedEvent& InEvent);

    FString StructPropertyPath;
    TSharedPtr<IPropertyHandle> EnvelopeTypePropertyHandle;
};
```

```cpp
// MyMetaSoundNodeCustomization.cpp
#include "MyMetaSoundNodeCustomization.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"

FMyGranularNodeCustomization::FMyGranularNodeCustomization(
    TSharedPtr<IPropertyHandle> InStructProperty,
    TWeakObjectPtr<UMetasoundEditorGraphNode> InNode)
    : FMetaSoundNodeConfigurationCustomization(InStructProperty, InNode)
{
    // 获取包络类型属性句柄
    EnvelopeTypePropertyHandle = InStructProperty->GetChildHandle(
        GET_MEMBER_NAME_CHECKED(FMyGranularConfig, EnvelopeType));
    
    if (EnvelopeTypePropertyHandle.IsValid())
    {
        // 监听属性变化以触发节点图刷新
        EnvelopeTypePropertyHandle->SetOnPropertyValueChanged(
            FSimpleDelegate::CreateSP(this, 
                &FMyGranularNodeCustomization::OnEnvelopeTypeChanged));
    }
}

void FMyGranularNodeCustomization::OnChildRowAdded(IDetailPropertyRow& ChildRow)
{
    // 自定义特定属性行的显示（如隐藏、替换编辑器控件等）
    TSharedPtr<IPropertyHandle> Property = ChildRow.GetPropertyHandle();
    
    if (Property.IsValid() && Property == EnvelopeTypePropertyHandle)
    {
        // 可在此替换默认编辑器为自定义 Widget
    }
}

void FMyGranularNodeCustomization::OnEnvelopeTypeChanged(
    const FPropertyChangedEvent& InEvent)
{
    // 通知 MetaSound 节点配置已变更，触发图重新编译
    if (TWeakObjectPtr<UMetasoundEditorGraphNode> Node = GetEditingNode())
    {
        Node->SetNodeConfigurationOutdated();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心系统，此插件的所有实验性功能都构建在其之上 |
| `MetasoundEditor` | MetaSound 编辑器模块，用于节点配置自定义和编辑器扩展 |

> 无其他特殊依赖。各 Runtime 模块仅依赖 `CoreUObject`（标准依赖），Editor 模块依赖 MetaSound 编辑器基础设施。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 新增实验性 CAT Wave 波形资产类型 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 新增 CAT 乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 新增 CAT 梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待提交变更列表中恢复，具体变更内容未详细说明 |

### 维护评价

- **活跃维护中**：创建于 2025 年 4 月，最近更新在 2026 年 5 月，开发节奏密集（连续数天有提交）
- **开发方向明确**：近期集中在 CAT（Channel Agnostic Types）功能的构建上，新增了 Wave 容器、Multiply 节点、Ladder Filter 节点等
- **Epic 官方维护**：由 Epic Games 的 MetaSound 团队直接维护，有 JIRA 工单跟踪（UE-273384）
- **实验性警告**：标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，API 不稳定，功能随时可能被修改、移除或合并到正式 MetaSound 插件
- **推荐使用**：适合希望提前体验 MetaSound 新特性的技术用户和节点开发者，但**不推荐用于生产环境**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [MetaSound 正式插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)（本插件的功能最终会合并到此处）