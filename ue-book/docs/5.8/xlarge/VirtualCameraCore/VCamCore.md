# Virtual Camera Core

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VCamCore` (Runtime), `VCamCoreEditor` (Runtime), `VCamBlueprintNodes` (Runtime), `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

VirtualCameraCore 插件是一个为虚拟制作（Virtual Production）工作流设计的核心运行时框架。它的主要目的是提供一套完整的 MVC（Model-View-Controller）架构，用于通过物理设备（如平板电脑、遥控器等）或软件界面实时控制和预览 Unreal Engine 内的 CineCameraActor。

**解决的问题**：
1.  **设备抽象化**：为各种物理输入设备提供统一的输入处理和设备管理接口，使开发者无需关心底层设备差异。
2.  **相机控制逻辑**：将相机控制逻辑（如移动、变焦、对焦）封装为可复用的“修饰器”（Modifier），便于组合和定制。
3.  **输出与预览**：将相机画面和自定义 UI 通过多种方式输出到外部设备或窗口（如像素流、远程会话、编辑器视口），实现实时预览。
4.  **多视口管理**：管理多个视口的锁定、分辨率和所有权，确保在复杂的多虚拟相机场景下系统能正确工作。
5.  **多用户协作**：内置与 Unreal 的多用户编辑系统集成的逻辑，方便在多人协作场景中同步相机状态。

简而言之，这个插件是虚拟制作管线中连接物理世界（设备）和数字世界（引擎相机）的核心桥梁。

## 使用场景

-   **电影/电视预览**：导演或摄影师使用 iPad 等设备作为虚拟监视器，实时查看 Unreal 场景中设定的虚拟机位画面，并调整相机参数。
-   **实时预览**：在大型 LED 虚拟拍摄现场，将 Unreal 的实时渲染画面通过此插件流送到现场监视器，让导演看到接近最终合成的画面。
-   **多机位预览**：同时监控和控制场景中多个虚拟摄像机的输出，例如在编辑器中为每个摄像机分配一个视口（Viewport 1-4）并分别锁定。
-   **自定义控制界面**：开发者可以使用 UMG 创建自定义的虚拟相机控制界面（如滑块、按钮），并通过连接系统（Connection System）将这些 UI 元素与修饰器（Modifier）的功能绑定。
-   **输入设备映射**：将游戏手柄、MIDI 控制器等物理输入设备的按键/摇杆，映射为虚拟相机控制动作。

## 蓝图用法

该插件的核心蓝图操作主要围绕 `UVCamComponent` 及其管理的“修饰器栈”（Modifier Stack）和“输出提供者栈”（Output Provider Stack）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Modifier` | 向修饰器栈中添加一个指定类的修饰器实例。 | `UVCamComponent` |
| `Remove Modifier` | 从修饰器栈中移除指定的修饰器实例。 | `UVCamComponent` |
| `Get Modifier By Name` | 通过名称从栈中获取一个修饰器实例。 | `UVCamComponent` |
| `Add Output Provider` | 向输出提供者栈中添加一个指定类的输出提供者实例。 | `UVCamComponent` |
| `Set Active` | 启用或禁用一个输出提供者。 | `UVCamOutputProviderBase` |
| `Set Input Profile From Name` | 为组件应用一个预定义的输入配置文件。 | `UVCamComponent` |
| `Inject Input For Action` | 以代码方式向指定的输入动作注入一个输入值。 | `UVCamComponent` |
| `Get Connection By Name` | 从 UVCamWidget 中获取指定名称的连接信息。 | `UVCamUIFunctionLibrary` |
| `Is Connected By Name` | 查询指定连接是否成功建立。 | `UVCamUIFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **创建虚拟相机**：
    - 将 `VCamBaseActor` 拖入场景，它已内置了 `UVCamComponent` 和 `CineCameraComponent`。
    - 在 `UVCamComponent` 的“细节”面板中，点击“修饰器”旁的“+”号添加一个内置的或自定义的修饰器（如控制相机旋转的修饰器）。
    - 在“输出提供者”旁添加一个输出提供者，如 `VCamOutputRemoteSession`，用于将画面输出到设备。

2.  **绑定自定义 UI**：
    - 创建一个继承自 `UVCamWidget` 的 UMG Widget。
    - 在该 Widget 的“连接”（Connections）映射表中，为每个交互控件（如一个按钮）添加一个条目。
    - 在“细节”面板中，配置该连接的“目标修饰器名称”和“目标连接点名称”，将其指向步骤1中添加的修饰器和该修饰器上定义的连接点（Connection Point）。
    - 当游戏运行时，该 Widget 会尝试自动连接，按钮的点击事件就可以触发修饰器上绑定的输入动作（Input Action）。

## C++ 用法

主要使用 `VCamCore` 模块提供的类来扩展系统，如创建自定义修饰器或输出提供者。

### 头文件引入

```cpp
// 访问核心组件和基类
#include "VCamComponent.h"
#include "Modifier/VCamModifier.h"
#include "Output/VCamOutputProviderBase.h"
// 访问连接系统（如果需要创建自定义Widget）
#include "UI/VCamConnectionStructs.h"
```

### 基本用法

以下示例展示了如何创建一个简单的自定义修饰器，该修饰器在每一帧根据输入旋转关联的相机。

**自定义修饰器头文件 (.h)**:
```cpp
// 文件路径: YourPlugin/Source/YourPlugin/Public/Modifiers/MyRotationModifier.h
#pragma once

#include "Modifier/VCamModifier.h"
#include "MyRotationModifier.generated.h"

UCLASS(BlueprintType, EditInlineNew)
class YOURPLUGIN_API UMyRotationModifier : public UVCamModifier
{
    GENERATED_BODY()

public:
    // 暴露给蓝图和编辑器的属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Modifier")
    FRotator RotationSpeed = FRotator(0.f, 30.f, 0.f); // 每秒旋转30度

    // 重写Apply函数，这是每帧调用的核心逻辑
    virtual void Apply(UVCamModifierContext* Context, UCineCameraComponent* CameraComponent, const float DeltaTime) override;

    // 用于连接系统的输入动作（可选）
    UPROPERTY(EditAnywhere, Category = "VCam Connection Points")
    TMap<FName, FVCamModifierConnectionPoint> ConnectionPoints;
};
```

**自定义修饰器实现文件 (.cpp)**:
```cpp
// 文件路径: YourPlugin/Source/YourPlugin/Private/Modifiers/MyRotationModifier.cpp
#include "Modifiers/MyRotationModifier.h"

void UMyRotationModifier::Apply(UVCamModifierContext* Context, UCineCameraComponent* CameraComponent, const float DeltaTime)
{
    if (CameraComponent && IsEnabled())
    {
        // 获取当前的旋转
        FRotator CurrentRotation = CameraComponent->GetRelativeRotation();
        // 根据速度和增量时间计算新旋转
        FRotator NewRotation = CurrentRotation + (RotationSpeed * DeltaTime);
        // 应用新旋转
        CameraComponent->SetRelativeRotation(NewRotation);
    }
}
```

### 进阶用法

结合输入系统和连接点，创建可响应UI控件的修饰器。

**带连接点的修饰器头文件 (.h)**:
```cpp
UCLASS(BlueprintType, EditInlineNew)
class UMyControllableModifier : public UVCamModifier
{
    GENERATED_BODY()

public:
    // 这个连接点将暴露一个名为“ZoomAction”的输入动作
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VCam Connection Points")
    FVCamModifierConnectionPoint ZoomConnectionPoint;

    // 当通过UI触发“ZoomAction”时调用的函数
    UFUNCTION()
    void OnZoomActionTriggered(const FInputActionValue& Value);

    virtual void Initialize(UVCamModifierContext* Context, UInputComponent* InputComponent) override;
    virtual void Deinitialize() override;

private:
    // 存储绑定了动作的委托句柄
    FDelegateHandle ZoomActionDelegateHandle;
};
```

**实现 (.cpp)**:
```cpp
void UMyControllableModifier::Initialize(UVCamModifierContext* Context, UInputComponent* InputComponent)
{
    Super::Initialize(Context, InputComponent);

    // 为连接点配置的输入动作绑定回调
    if (ZoomConnectionPoint.AssociatedAction && InputComponent)
    {
        ZoomActionDelegateHandle = InputComponent->BindAction(ZoomConnectionPoint.AssociatedAction, ETriggerEvent::Triggered, this, &UMyControllableModifier::OnZoomActionTriggered).GetHandle();
    }
}

void UMyControllableModifier::Deinitialize()
{
    if (InputComponent && ZoomActionDelegateHandle.IsValid())
    {
        InputComponent->RemoveActionBinding(ZoomConnectionPoint.AssociatedAction, ZoomActionDelegateHandle);
        ZoomActionDelegateHandle.Reset();
    }
    Super::Deinitialize();
}

void UMyControllableModifier::OnZoomActionTriggered(const FInputActionValue& Value)
{
    // Value 可能是 bool（按下）、Axis1D（浮点数）、Axis2D（二维向量）等
    float ZoomDelta = Value.Get<float>();
    // 执行缩放逻辑...
}
```

## Demo 示例

一个最小的、可编译的示例，展示如何创建自定义修饰器和输出提供者。

**自定义输出提供者 (.h)**:
```cpp
// 文件路径: YourPlugin/Source/YourPlugin/Public/Output/VCamOutputLog.h
#pragma once

#include "Output/VCamOutputProviderBase.h"
#include "VCamOutputLog.generated.h"

UCLASS(BlueprintType)
class YOURPLUGIN_API UVCamOutputLog : public UVCamOutputProviderBase
{
    GENERATED_BODY()
public:
    UVCamOutputLog();

    // 重写 Tick，在输出启用时打印日志
    virtual void Tick(const float DeltaTime) override;

    // 重写 OnActivate 和 OnDeactivate 来管理状态
    virtual void OnActivate() override;
    virtual void OnDeactivate() override;

private:
    bool bIsOutputting = false;
};
```

**实现 (.cpp)**:
```cpp
// 文件路径: YourPlugin/Source/YourPlugin/Private/Output/VCamOutputLog.cpp
#include "Output/VCamOutputLog.h"
#include "VCamComponent.h"

UVCamOutputLog::UVCamOutputLog()
{
    // 设置显示类型为无UI叠加
    DisplayType = EViewportWidgetOverlay_DisplayType::Inactive;
}

void UVCamOutputLog::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (IsOutputting() && bIsOutputting)
    {
        // 获取关联的相机组件
        UCineCameraComponent* Camera = GetVCamComponent()->GetTargetCamera();
        if (Camera)
        {
            UE_LOG(LogTemp, Log, TEXT("VCam Output: Camera FOV is %f"), Camera->FieldOfView);
        }
    }
}

void UVCamOutputLog::OnActivate()
{
    Super::OnActivate();
    bIsOutputting = true;
    UE_LOG(LogTemp, Log, TEXT("VCamOutputLog Activated"));
}

void UVCamOutputLog::OnDeactivate()
{
    bIsOutputting = false;
    UE_LOG(LogTemp, Log, TEXT("VCamOutputLog Deactivated"));
    Super::OnDeactivate();
}
```

**使用方式**：
1.  编译你的插件。
2.  在 `UVCamComponent` 的“输出提供者”数组中，添加一个 `VCamOutputLog` 类型的元素。
3.  启用该输出提供者并运行游戏，控制台将每帧打印一次相机的视场角信息。

## 模块依赖

要使用此插件，你的模块需要依赖 `VCamCore` 模块。

| 模块 | 用途 |
|---|---|
| `VCamCore` | 提供 `UVCamComponent`、`UVCamModifier`、`UVCamOutputProviderBase` 等核心类。 |

其他模块（如 `VCamCoreEditor`、`PixelStreamingVCam`）是插件内部的实现细节，通常不需要外部模块直接依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复了在PIE/模拟运行时可能出现的崩溃问题 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将多个虚拟制作资产迁移至新目录并重新分类，优化资产组织结构 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，统一日志格式 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏Widget功能从实验性状态迁移至独立的、更稳定的视口Widget覆盖插件 |

### 维护评价

-   **活跃维护**：插件创建于2024年初，最近一次提交在2026年5月，且近几个月内有多次功能性更新（资产重组、bug修复），表明 Epic Games 正在积极维护。
-   **实验性状态**：尽管 `.uplugin` 中 `IsBetaVersion` 为 `true`，但从更新日志看，其功能已相当成熟，正在从实验性向核心功能迁移（如将 `UVPFullScreenWidget` 迁出）。
-   **发展趋势**：作为虚拟制作管线的核心组件，预计将长期支持并不断完善。近期更新显示其架构在持续优化（如资产分类调整）。
-   **推荐使用**：对于虚拟制作项目，特别是需要从外部设备控制和预览相机的场景，推荐使用此插件。由于其实验性标签，建议在项目初期集成，并关注后续版本更新。

**注意**：该插件默认未启用（`EnabledByDefault=false`），使用前需要在项目设置或 `.uproject` 文件中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore)
-   官方文档：暂无专门文档
-   测试用例：插件源码中的测试文件分散在各模块的 `Private/Tests` 或 `Public/Tests` 目录下，例如 `Engine/Plugins/VirtualProduction/VirtualCameraCore/Source/VCamCore/Private/Tests/`。