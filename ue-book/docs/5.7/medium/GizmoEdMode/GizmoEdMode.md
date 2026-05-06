# Gizmo Editor Mode

> Editor mode to manage InteractiveToolFramework based global TRS gizmos

| 属性 | 值 |
|---|---|
| 中文名 | 变换 Gizmo 模式 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GizmoEdMode` (Editor), `LightGizmos` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoEdMode) | |

## 用途

该插件提供了一个编辑器模式 `UGizmoEdMode`，用于在资产编辑器（如 StaticMesh 编辑器、SkeletalMesh 编辑器等）中管理基于 InteractiveToolFramework 的全局 TRS（平移、旋转、缩放）小工具（Gizmo）。它通过可扩展的工厂接口 `IAssetEditorGizmoFactory` 允许不同资产类型注册自己的 Gizmo 生成逻辑，从而替代或增强标准的编辑器 Gizmo 交互。默认工厂 `UDefaultAssetEditorGizmoFactory` 为一般选择提供基础的 TRS Gizmo。

**核心功能：**

- 统一管理资产编辑器内的全局变换 Gizmo。
- 提供工厂模式，支持自定义 Gizmo 生成与配置。
- 支持网格对齐（Grid Snapping）配置。
- 与 UEdMode 集成，自动响应选择变化并重建 Gizmo。

## 使用场景

- 你在开发一个资产编辑器插件，需要为特定类型的对象提供自定义的变换交互（例如，为骨骼或碰撞体提供专用 Gizmo）。
- 你需要全局统一替换标准的编辑器 Gizmo 行为（例如，修改 Gizmo 的外观或输入处理逻辑）。
- 你正在使用 InteractiveToolFramework 构建工具，并希望它在资产编辑器环境中与现有选择机制无缝配合。

## 蓝图用法

该插件完全使用 C++ 实现，**无公开的蓝图可调用 API**。所有核心逻辑通过接口和编辑器模式在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "GizmoEdMode.h"
#include "AssetEditorGizmoFactory.h"
```

### 基本用法

以下示例演示如何在自定义资产编辑器模式下激活 `UGizmoEdMode` 并注册一个自定义 Gizmo 工厂。此代码通常在你的编辑器模式或模块启动时执行。

```cpp
// 在你的编辑器模式初始化中
void UMyEditorMode::Enter()
{
    Super::Enter();

    // 获取 GizmoEdMode 实例并添加工厂
    if (UGizmoEdMode* GizmoMode = Cast<UGizmoEdMode>(GetWorld()->GetSubsystem<UEdModeSubsystem>()->GetActiveMode(UGizmoEdMode::StaticClass())))
    {
        // 注册自定义工厂（假设 UMyGizmoFactory 实现了 IAssetEditorGizmoFactory）
        GizmoMode->AddFactory(TScriptInterface<IAssetEditorGizmoFactory>(NewObject<UMyGizmoFactory>()));
    }
}
```

### 自定义 Gizmo 工厂

实现 `IAssetEditorGizmoFactory` 接口以提供自定义 Gizmo：

```cpp
// MyGizmoFactory.h
#pragma once
#include "AssetEditorGizmoFactory.h"
#include "MyGizmoFactory.generated.h"

UCLASS()
class UMyGizmoFactory : public UObject, public IAssetEditorGizmoFactory
{
    GENERATED_BODY()
public:
    // 判断当前选择是否适用此工厂
    virtual bool CanBuildGizmoForSelection(FEditorModeTools* ModeTools) const override;
    
    // 构建 Gizmo 数组
    virtual TArray<UInteractiveGizmo*> BuildGizmoForSelection(
        FEditorModeTools* ModeTools,
        UInteractiveGizmoManager* GizmoManager) const override;
    
    // 返回优先级（影响多个工厂时的选择）
    virtual EAssetEditorGizmoFactoryPriority GetPriority() const override 
    { 
        return EAssetEditorGizmoFactoryPriority::Normal; 
    }
    
    // 配置网格吸附
    virtual void ConfigureGridSnapping(
        bool bGridEnabled,
        bool bRotGridEnabled,
        const TArray<UInteractiveGizmo*>& Gizmos) const override;
};
```

```cpp
// MyGizmoFactory.cpp
#include "MyGizmoFactory.h"
#include "EditorModeTools.h"
#include "InteractiveGizmoManager.h"
#include "BaseGizmos/CombinedTransformGizmo.h"

bool UMyGizmoFactory::CanBuildGizmoForSelection(FEditorModeTools* ModeTools) const
{
    // 当选定对象是你的目标类型时返回 true
    return ModeTools->GetSelectedActors()->Num() > 0;
}

TArray<UInteractiveGizmo*> UMyGizmoFactory::BuildGizmoForSelection(
    FEditorModeTools* ModeTools,
    UInteractiveGizmoManager* GizmoManager) const
{
    TArray<UInteractiveGizmo*> Gizmos;
    // 创建 CombinedTransformGizmo 并添加到 GizmoManager
    UCombinedTransformGizmo* Gizmo = GizmoManager->CreateGizmo<UCombinedTransformGizmo>();
    if (Gizmo)
    {
        // 配置 Gizmo 行为...
        Gizmos.Add(Gizmo);
    }
    return Gizmos;
}

void UMyGizmoFactory::ConfigureGridSnapping(
    bool bGridEnabled,
    bool bRotGridEnabled,
    const TArray<UInteractiveGizmo*>& Gizmos) const
{
    for (UInteractiveGizmo* Gizmo : Gizmos)
    {
        if (UCombinedTransformGizmo* Combined = Cast<UCombinedTransformGizmo>(Gizmo))
        {
            Combined->bSnapToWorldGrid = bGridEnabled;
            Combined->bSnapToWorldRotGrid = bRotGridEnabled;
        }
    }
}
```

**注册工厂**：推荐在模块启动时通过 `UEditorModeSubsystem` 获取 GizmoEdMode 实例并调用 `AddFactory`（如上基本用法所示）。对于全局插件，可监听编辑器模式激活事件。

### 进阶用法

- **多工厂协作**：通过 `GetPriority()` 控制工厂选择顺序。高优先级工厂会优先于低优先级工厂被使用。
- **自定义 Gizmo 生命周期**：`UGizmoEdMode` 会在选择变化时自动销毁重建 Gizmo（调用 `DestroyGizmo` 和 `RecreateGizmo`）。工厂无需管理生命周期，只需保证 `BuildGizmoForSelection` 返回的 Gizmo 已正确初始化。
- **网格吸附联动**：编辑器中的网格吸附设置会自动调用所有活跃工厂的 `ConfigureGridSnapping` 方法，工厂可在此处调整 Gizmo 的吸附行为。

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建并使用自定义工厂。

**MyGizmoFactoryDemo.h**:
```cpp
#pragma once
#include "AssetEditorGizmoFactory.h"
#include "CoreMinimal.h"
#include "MyGizmoFactoryDemo.generated.h"

UCLASS()
class UMyGizmoFactoryDemo : public UObject, public IAssetEditorGizmoFactory
{
    GENERATED_BODY()
public:
    virtual bool CanBuildGizmoForSelection(FEditorModeTools* ModeTools) const override;
    virtual TArray<UInteractiveGizmo*> BuildGizmoForSelection(
        FEditorModeTools* ModeTools,
        UInteractiveGizmoManager* GizmoManager) const override;
    virtual EAssetEditorGizmoFactoryPriority GetPriority() const override 
    { 
        return EAssetEditorGizmoFactoryPriority::Normal; 
    }
    virtual void ConfigureGridSnapping(
        bool bGridEnabled,
        bool bRotGridEnabled,
        const TArray<UInteractiveGizmo*>& Gizmos) const override;
};
```

**MyGizmoFactoryDemo.cpp**:
```cpp
#include "MyGizmoFactoryDemo.h"
#include "EditorModeTools.h"
#include "InteractiveGizmoManager.h"
#include "BaseGizmos/CombinedTransformGizmo.h"

bool UMyGizmoFactoryDemo::CanBuildGizmoForSelection(FEditorModeTools* ModeTools) const
{
    // 仅当选择非空时激活
    return ModeTools->GetSelectedActors()->Num() > 0;
}

TArray<UInteractiveGizmo*> UMyGizmoFactoryDemo::BuildGizmoForSelection(
    FEditorModeTools* ModeTools,
    UInteractiveGizmoManager* GizmoManager) const
{
    TArray<UInteractiveGizmo*> Gizmos;
    UCombinedTransformGizmo* Gizmo = GizmoManager->CreateGizmo<UCombinedTransformGizmo>();
    if (Gizmo)
    {
        // 可以在此设置 Gizmo 的特定属性
        Gizmos.Add(Gizmo);
    }
    return Gizmos;
}

void UMyGizmoFactoryDemo::ConfigureGridSnapping(
    bool bGridEnabled,
    bool bRotGridEnabled,
    const TArray<UInteractiveGizmo*>& Gizmos) const
{
    for (UInteractiveGizmo* Gizmo : Gizmos)
    {
        if (UCombinedTransformGizmo* Combined = Cast<UCombinedTransformGizmo>(Gizmo))
        {
            Combined->bSnapToWorldGrid = bGridEnabled;
            Combined->bSnapToWorldRotGrid = bRotGridEnabled;
        }
    }
}
```

**在模块启动时注册**（示例代码，假设在 `FMyModule::StartupModule` 中）:
```cpp
void FMyModule::StartupModule()
{
    // 延迟到编辑器模式可用时注册
    IEditorModeModule& EdModeModule = FModuleManager::LoadModuleChecked<IEditorModeModule>("EditorMode");
    // 注册你的编辑器模式（如果尚未注册）
    // ...

    // 获取 GizmoEdMode 并添加工厂（可能需要等待模式激活）
    if (GEditor)
    {
        GEditor->GetEditorSubsystem<UEditorModeSubsystem>()->OnActivateMode.AddLambda([](UEdMode* InMode)
        {
            if (UGizmoEdMode* GizmoMode = Cast<UGizmoEdMode>(InMode))
            {
                GizmoMode->AddFactory(TScriptInterface<IAssetEditorGizmoFactory>(NewObject<UMyGizmoFactoryDemo>()));
            }
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 提供 `UInteractiveGizmo`、`UInteractiveGizmoManager` 等基础类 |
| `UnrealEd` | 提供 `UEdMode`、`FEditorModeTools` 等编辑器框架 |
| `AssetsTools` | 提供资产编辑器的选择机制（隐含依赖） |

> 注意：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `InputCore` 等标准模块未列出，因为它们是几乎所有编辑器模块的基本依赖。

## 维护状态

### 近期更新

```
- 2025-05-31 52e3dac1 — Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types
- 2025-03-05 7ab43c2f — Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd
- 2025-02-02 b63cde15 — [Truncation Warnings] Enable truncation warnings in build.cs files for fixed modules
- 2025-01-28 191ad109 — [Truncation Warnings] Fix warnings in GizmoEdMode plugin modules
- 2024-11-10 66e9bb39 — Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
```

### 维护评价

- **创建时间**：2024-11-10（UE 5.5 开发周期中）。
- **活跃度**：最近半年内有多次提交，包括头文件清理、弃用警告修复、编译警告修正。表明 Epic 在持续维护该插件以适应引擎 API 变化。
- **状态**：该插件仍标记为 `Experimental`，但功能稳定且被内部使用。没有发现废弃或不可用的迹象。
- **推荐使用**：✅ 推荐用于需要自定义资产编辑器 Gizmo 的场景。由于是实验性，接口可能在未来发生变化，但基础设计相对成熟。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoEdMode)
- [测试用例（部分位于 Engine/Tests 下）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoEdMode/Source/GizmoEdMode/Private/Tests)（如果存在）