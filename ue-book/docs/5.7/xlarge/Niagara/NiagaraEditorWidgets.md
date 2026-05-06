# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 特效系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器 UI 组件、蓝图节点、渲染器细节定制） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-03-01（推断） |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara) | |

---

## 用途

Niagara 是 Unreal Engine 的新一代 VFX 系统，用于创建粒子、光束、流体等视觉效果。它提供了基于节点编辑的脚本化粒子系统，支持 GPU 和 CPU 模拟，以及高度的自定义能力。

`NiagaraEditorWidgets` 模块是 Niagara 编辑器的一部分，专门提供用于编辑器界面的可复用 Widget 组件。它为 `NiagaraEditor` 模块提供 UI 组件（如 Stack 视图、曲线编辑器、渲染器细节面板、缩放预览等），使得 Niagara 的编辑器界面更加模块化和可定制。该模块不包含运行时逻辑，仅在编辑器环境下工作。

---

## 使用场景

- 你正在开发 Niagara 编辑器扩展或自定义细节面板 → 引用 `NiagaraEditorWidgets` 中的类。
- 你需要在 Niagara 编辑器中添加新的 UI 控件（如参数提示、渲染器缩略图、缩放设置面板） → 使用 `NiagaraEditorWidgets` 中的 SCompoundWidget 子类。
- 你需要为 Niagara 数据接口（Data Interface）编写自定义的属性面板 → 继承 `FNiagaraDataInterfaceDetailsBase` 并实现详细信息定制。

---

## 蓝图用法

`NiagaraEditorWidgets` 是编辑器模块，**不提供运行时蓝图可调用 API**。不过，Niagara 插件本身包含 `NiagaraBlueprintNodes` 模块，该模块提供 BPT（BlueprintCallable）节点用于运行时与 Niagara 系统交互。但由于本模块聚焦编辑器小部件，以下列出仅与编辑器功能相关的蓝图节点（部分）。

### 编辑器功能节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Niagara System` | 从 UObject 获取 Niagara 系统资源 | `UNiagaraFunctionLibrary` (核心) |
| `Spawn Niagara System` | 在世界中生成 Niagara 粒子系统 | `UNiagaraFunctionLibrary` (核心) |
| `Set Niagara Variable` | 设置 Niagara 系统参数（编辑器预览） | `UNiagaraFunctionLibrary` (核心) |

> 注意：`NiagaraEditorWidgets` 本身不暴露蓝图节点。上述节点属于 Niagara 核心运行时，但在编辑器中使用以预览效果。

---

## C++ 用法

### 头文件引入

```cpp
// 通常需要包含 NiagaraEditorWidgets 模块的头文件
#include "NiagaraEditorWidgetsStyle.h"
#include "NiagaraOverviewGraphNodeFactory.h"
#include "DetailCustomizations/NiagaraDataInterfaceSkeletalMeshDetails.h"
```

### 基本用法

#### 注册自定义细节定制

```cpp
// 在模块 StartupModule 中注册
FPropertyEditorModule& PropertyEditorModule = FModuleManager::GetModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyEditorModule.RegisterCustomClassLayout(
    UNiagaraDataInterfaceSkeletalMesh::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FNiagaraDataInterfaceSkeletalMeshDetails::MakeInstance)
);
```

来源：`Source/NiagaraEditorWidgets/Private/DetailCustomizations/NiagaraDataInterfaceSkeletalMeshDetails.h`

#### 使用 Niagara 曲线编辑器 Widget

```cpp
// 创建曲线概述 Widget
TSharedRef<FNiagaraSystemViewModel> SystemViewModel = ...;
SAssignNew(CurveOverview, SNiagaraCurveOverview, SystemViewModel);
// 将其放入父容器
ParentContainer->AddSlot() [ CurveOverview.ToSharedRef() ];
```

来源：`Source/NiagaraEditorWidgets/Private/SNiagaraCurveOverview.h`

#### 替换默认图节点工厂

```cpp
// 在 Niagara 编辑器模块中设置节点工厂
TSharedPtr<FNiagaraOverviewGraphNodeFactory> Factory = MakeShared<FNiagaraOverviewGraphNodeFactory>();
SGraphEditor::SetNodeFactory(Factory);
```

来源：`Source/NiagaraEditorWidgets/Private/NiagaraOverviewGraphNodeFactory.h`

### 进阶用法

#### 为数据接口实现自定义细节面板

继承 `FNiagaraDataInterfaceDetailsBase` 并重写 `CustomizeDetails`：

```cpp
class FMyCustomDIDetails : public FNiagaraDataInterfaceDetailsBase
{
public:
    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override
    {
        // 添加自定义类别
        IDetailCategoryBuilder& MyCategory = DetailBuilder.EditCategory("MyCustomCategory");
        // 添加属性
        TSharedRef<IPropertyHandle> Property = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UNiagaraDataInterfaceMyCustom, MyParam));
        MyCategory.AddProperty(Property);
    }

    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyCustomDIDetails);
    }
};
```

#### 创建缩放预览设置 Widget

```cpp
UNiagaraSystemScalabilityViewModel* ScalabilityViewModel = ...;
SAssignNew(ScalabilityPreview, SNiagaraScalabilityPreviewSettings, *ScalabilityViewModel);
// 添加到面板
SettingsBox->AddSlot() [ ScalabilityPreview.ToSharedRef() ];
```

来源：`Source/NiagaraEditorWidgets/Private/SNiagaraScalabilityPreviewSettings.h`

---

## Demo 示例

以下是一个在自定义 Niagara 编辑器模块中注册细节定制的最小示例。

**MyNiagaraEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleInterface.h"

class FMyNiagaraEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyNiagaraEditorModule.cpp**
```cpp
#include "MyNiagaraEditorModule.h"
#include "PropertyEditorModule.h"
#include "NiagaraDataInterfaceSkeletalMesh.h"
#include "NiagaraDataInterfaceSkeletalMeshDetails.h"

void FMyNiagaraEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    // 注册自定义细节定制
    PropertyModule.RegisterCustomClassLayout(
        UNiagaraDataInterfaceSkeletalMesh::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(&FNiagaraDataInterfaceSkeletalMeshDetails::MakeInstance)
    );

    PropertyModule.NotifyCustomizationModuleChanged();
}

void FMyNiagaraEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("PropertyEditor"))
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::GetModuleChecked<FPropertyEditorModule>("PropertyEditor");
        PropertyModule.UnregisterCustomClassLayout(UNiagaraDataInterfaceSkeletalMesh::StaticClass()->GetFName());
    }
}

IMPLEMENT_MODULE(FMyNiagaraEditorModule, MyNiagaraEditor);
```

---

## 模块依赖

`NiagaraEditorWidgets` 的独特依赖（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心 Niagara 运行时类型，如粒子系统、数据接口 |
| `NiagaraEditor` | 编辑器 ViewModel 和 Stack 模型 |
| `AssetRegistry` | 资产数据用于预览和缩放设置 |
| `CurveEditor` | 曲线编辑功能（`SNiagaraCurveOverview`） |
| `GraphEditor` | 用于 `SNiagaraOverviewGraph` |
| `PropertyEditor` | 细节面板定制（`IDetailCustomization`） |

**注意**：若你开发的是编辑器模块（如 `UncookedOnly` 类型），需确保已添加 `Niagara`, `NiagaraEditor`, `NiagaraEditorWidgets` 到 PublicDependencyModuleNames。

---

## 维护状态

### 近期更新

- 2025-10-22 `5d0cd83c` Fix for issue with access to freed Niagara Components during cleanup.
- 2025-10-22 `3f549682` Fixed issue with lingering NDC data when there are updates with no data from the CPU.
- 2025-10-21 `6ac05a79` Added off-by-default workaround for Niagara crash we hit in internal testing.
- 2025-10-17 `f6546371` Fix issue caused by mis-matched GT and RT ticks causing NDC data to be effectively lost from the POV.
- 2025-10-16 `566219ca` [Backout] - CL47013072

### 维护评价

- **创建时间**：Niagara 系统约 2018 年引入，`NiagaraEditorWidgets` 模块随 Niagara 编辑器一同发布。
- **近期更新**：2025 年 10 月仍在活跃修复（内存泄露、数据通道问题等），显示积极维护。
- **是否活跃维护**：是。从 2025 年 10 月连续多次 commits 可见。
- **已知问题或限制**：模块主要为编辑器服务，不适用于运行时；部分 Widget（如细节定制）依赖 `PropertyEditor` 模块。
- **推荐使用**：✅ 推荐。功能完善，Epic 官方持续维护，适合大多数 Niagara 编辑器扩展场景。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/niagara-effects-system/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Test)