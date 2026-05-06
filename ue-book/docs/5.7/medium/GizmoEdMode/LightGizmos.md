# Gizmo Editor Mode

> Editor mode to manage InteractiveToolFramework based global TRS gizmos

| 属性 | 值 |
|---|---|
| 中文名 | Gizmo 编辑器模式 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GizmoEdMode` (Editor), `LightGizmos` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoEdMode) | |

## 用途

该插件是实验性的编辑器模式，用于管理基于 InteractiveToolFramework 的全局变换（TRS）Gizmo。  
核心模块 `LightGizmos` 为场景中的光源（方向光、点光、聚光灯）提供了专门的交互式 Gizmo，允许用户通过拖拽视口中的手柄直接调整灯光属性（如方向、衰减半径、锥角），无需切换至细节面板。  
它解决了传统灯光编辑不够直观、操作效率低的问题，提供了所见即所得的编辑体验。

## 使用场景

- 在关卡中快速调整方向光的照射角度，直接拖拽世界 Z 轴旋转圆环或 Y 轴箭头。
- 修改点光的衰减半径，通过可缩放球体 Gizmo 实时调整。
- 调整聚光灯的内外锥角和衰减范围，使用圆锥 Gizmo 和缩放杆。
- 作为自定义编辑器工具的一部分，利用工厂模式为特定光源类型构建 Gizmo。

## 蓝图用法

此模块专注于编辑器 C++ 实现，不提供公开的蓝图可调用节点或可蓝图继承的类。蓝图无法直接操作这些 Gizmo，但可以通过编辑器脚本间接触发，或通过自定义 UEditorMode 集成。

## C++ 用法

### 头文件引入

```cpp
#include "DirectionalLightGizmo.h"
#include "PointLightGizmo.h"
#include "SpotLightGizmo.h"
#include "ScalableConeGizmo.h"
#include "DirectionalLightGizmoFactory.h"
#include "PointLightGizmoFactory.h"
#include "SpotLightGizmoFactory.h"
#include "LightGizmosModule.h"
```

### 基本用法

通过工厂类为当前选择的光源自动构建 Gizmo（通常在编辑器模式中调用）：

```cpp
// 在 UEditorMode 或工具中注册工厂
void UMyEditorMode::Enter()
{
    // 获取 Gizmo 管理器
    UInteractiveGizmoManager* GizmoManager = GetModeManager()->GetInteractiveGizmoManager();

    // 注册工厂（通常由模块启动时自动注册，此处仅为示例）
    UDirectionalLightGizmoFactory* Factory = NewObject<UDirectionalLightGizmoFactory>();
    GizmoManager->RegisterGizmoFactory(Factory);
}
```

手动创建并配置单个方向光 Gizmo：

```cpp
// 头文件：Private/DirectionalLightGizmo.h
// GitHub 路径：Engine/Plugins/Experimental/GizmoEdMode/Source/LightGizmos/Private/DirectionalLightGizmo.h

UDirectionalLightGizmo* LightGizmo = NewObject<UDirectionalLightGizmo>();
LightGizmo->SetSelectedObject(MyDirectionalLight);   // 设置目标光源
LightGizmo->SetWorld(GetWorld());                     // 设置世界
LightGizmo->SetGizmoViewContext(MyViewContext);       // 设置视图上下文
LightGizmo->Setup();                                  // 初始化内部行为
```

### 进阶用法

使用 `UScalableConeGizmo` 创建自定义圆锥缩放 Gizmo（例如聚光灯内锥角调整）：

```cpp
// 头文件：Public/ScalableConeGizmo.h
// GitHub 路径：Engine/Plugins/Experimental/GizmoEdMode/Source/LightGizmos/Public/ScalableConeGizmo.h

// 创建圆锥 Gizmo
UScalableConeGizmo* ConeGizmo = NewObject<UScalableConeGizmo>();
ConeGizmo->SetTarget(TransformProxy);        // 绑定到变换代理
ConeGizmo->SetAngleDegrees(45.0f);           // 初始锥角（度）
ConeGizmo->SetLength(200.0f);                // 锥体高度
ConeGizmo->MaxAngle = 90.0f;
ConeGizmo->MinAngle = 1.0f;
ConeGizmo->ConeColor = FColor::Yellow;
ConeGizmo->UpdateAngleFunc = [](float NewAngle) {
    // 当锥角变化时更新光源属性
    MySpotLight->SetOuterConeAngle(FMath::DegreesToRadians(NewAngle));
};
ConeGizmo->Setup();
```

工厂类的完整应用（自动判断并构建）：

```cpp
// 头文件：Public/DirectionalLightGizmoFactory.h
// GitHub 路径：Engine/Plugins/Experimental/GizmoEdMode/Source/LightGizmos/Public/DirectionalLightGizmoFactory.h

// 实现 IAssetEditorGizmoFactory 接口
bool UDirectionalLightGizmoFactory::CanBuildGizmoForSelection(FEditorModeTools* ModeTools) const
{
    // 检测当前选中的是否为方向光
    // ...
}

TArray<UInteractiveGizmo*> UDirectionalLightGizmoFactory::BuildGizmoForSelection(
    FEditorModeTools* ModeTools, UInteractiveGizmoManager* GizmoManager) const
{
    // 创建 UDirectionalLightGizmo 并绑定到选中的方向光
    // 注册输入行为等
}
```

## Demo 示例

以下是一个最小示例，展示如何在自定义编辑器模式下激活方向光 Gizmo（仅示意核心逻辑）。

**MyDirectionalLightGizmoMode.h**
```cpp
#pragma once
#include "EdMode.h"
#include "DirectionalLightGizmo.h"

class UMyDirectionalLightGizmoMode : public UEdMode
{
    GENERATED_BODY()
public:
    virtual void Enter() override;
    virtual void Exit() override;

private:
    UDirectionalLightGizmo* ActiveGizmo = nullptr;
};
```

**MyDirectionalLightGizmoMode.cpp**
```cpp
#include "MyDirectionalLightGizmoMode.h"
#include "DirectionalLightGizmo.h"
#include "DirectionalLightGizmoFactory.h"
#include "InteractiveGizmoManager.h"

void UMyDirectionalLightGizmoMode::Enter()
{
    Super::Enter();

    // 获取当前选中的光源
    ADirectionalLight* Light = /* 从选择集中获取 */;
    if (!Light) return;

    // 创建 Gizmo
    ActiveGizmo = NewObject<UDirectionalLightGizmo>(GetGizmoManager());
    ActiveGizmo->SetSelectedObject(Light);
    ActiveGizmo->SetWorld(GetWorld());
    ActiveGizmo->SetGizmoViewContext(GetModeManager()->GetGizmoViewContext());
    ActiveGizmo->Setup();

    // 注册到 Gizmo 管理器
    GetGizmoManager()->AddActiveGizmo(ActiveGizmo);
}

void UMyDirectionalLightGizmoMode::Exit()
{
    if (ActiveGizmo)
    {
        ActiveGizmo->Shutdown();
        ActiveGizmo = nullptr;
    }
    Super::Exit();
}
```

> 注意：实际使用中应使用工厂类或更规范的注册流程。此示例仅展示最小概念。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 提供 UInteractiveGizmo 基类和行为框架 |
| `EditorInteractiveToolsFramework` | 编辑器级别的交互工具支持 |
| `UnrealEd` | 编辑器模式、视图上下文、资产选择 |
| `LevelEditor` | 与视口交互，获取世界和视图信息 |
| `GeometryCore`（可能依赖） | 几何计算，用于碰撞检测 |

其他常见依赖（Core、Engine、Slate 等）不再赘述。

## 维护状态

### 近期更新

- 2025-05-31 52e3dac1 — Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types
- 2025-03-05 7ab43c2f — Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd
- 2025-02-02 b63cde15 — [Truncation Warnings] Enable truncation warnings in build.cs files for fixed modules
- 2025-01-28 191ad109 — [Truncation Warnings] Fix warnings in GizmoEdMode plugin modules
- 2024-11-10 66e9bb39 — Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base

### 维护评价

该插件创建于 2024 年 11 月，至今约 1 年，仍处于 **实验性** 阶段。近期更新以代码修正、编译警告修复和模块迁移为主，无新增功能，表明团队在保持其与新引擎版本兼容。作为较新的实验性插件，其 API 可能仍有变动，但基本功能稳定。推荐在了解实验性风险的前提下，用于需要直观灯光编辑的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoEdMode)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/interactive-gizmos/)（Interactive Gizmo 通用文档）
- [LightGizmos 模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoEdMode/Source/LightGizmos/Public)