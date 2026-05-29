# Viewport Widget Overlay

> Adds a utility for overlaying a widget in the viewport.

| 属性 | 值 |
|---|---|
| 中文名 | 视口部件覆盖 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Shader .usf、后处理材质） |
| 模块 | `ViewportWidgetOverlay` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-03-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ViewportWidgetOverlay) | |

## 用途

该插件提供了在游戏视口上覆盖 UMG Widget 的能力，核心是 `UViewportWidgetOverlay` 类。它从实验性的 VPUtilities 插件中独立出来，以便其他插件（如 VCam、Pixel Streaming）能够在不依赖实验性插件的前提下使用全屏 Widget 覆盖功能。

插件支持三种渲染方式：

1. **Viewport 模式**：直接通过 Slate 在视口上叠加 Widget（适用于编辑器/PIE）
2. **PostProcessWithBlendMaterial 模式**：将 Widget 渲染到 RenderTarget，再通过后处理材质混合到画面中（仅覆盖变形压缩区域）
3. **PostProcessSceneViewExtension 模式**：通过 Scene View Extension 在后处理阶段渲染 Widget（覆盖整个视口，忽略变形压缩），适用于 Pixel Streaming 等场景

每种模式可以分别针对编辑器、PIE 和游戏三种环境独立配置。

## 使用场景

- 你在开发 Virtual Production 工作流，需要在视口上叠加自定义 UI 控件 → 用 ViewportWidgetOverlay
- 你需要为 Pixel Streaming 在整个画面上覆盖 Widget（包括黑边区域）→ 用 `PostProcessSceneViewExtension` 模式
- 你正在做 VCam 类工具，需要把 Widget 渲染到后处理管线中 → 用 `PostProcessWithBlendMaterial` 模式并设置自定义 PostProcess Settings 来源
- 你需要 Widget 在编辑器视口和游戏运行时分别以不同方式显示 → 通过 `SetDisplayTypes` 分别配置

## 蓝图用法

该插件的 `UViewportWidgetOverlay` 是一个 `UObject`，其属性在 Details 面板中可编辑，但本身不是 Actor/Component，不直接暴露大量 BlueprintCallable 节点。主要通过属性配置和 C++ 调用来使用。

### 核心属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `WidgetClass` | 要显示的 UMG Widget 类 | `UViewportWidgetOverlay` |
| `EditorDisplayType` | 编辑器环境下的显示模式 | `UViewportWidgetOverlay` |
| `GameDisplayType` | 游戏环境下的显示模式 | `UViewportWidgetOverlay` |
| `PIEDisplayType` | PIE 环境下的显示模式 | `UViewportWidgetOverlay` |
| `PostProcessMaterial` | 后处理材质 | `FViewportWidgetOverlay_PostProcessBase` |
| `PostProcessTintColorAndOpacity` | 色调和透明度 | `FViewportWidgetOverlay_PostProcessBase` |
| `PostProcessOpacityFromTexture` | 纹理透明度系数 (0-1) | `FViewportWidgetOverlay_PostProcessBase` |
| `bUseWidgetDrawSize` | 是否自定义渲染尺寸 | `FViewportWidgetOverlay_PostProcessBase` |
| `WidgetDrawSize` | Widget 渲染尺寸 | `FViewportWidgetOverlay_PostProcessBase` |
| `bReceiveHardwareInput` | 是否接收鼠标键盘输入 | `FViewportWidgetOverlay_PostProcessBase` |
| `RenderTargetBlendMode` | RenderTarget 混合模式 | `FViewportWidgetOverlay_PostProcessBase` |

### 使用示例（蓝图描述）

由于 `UViewportWidgetOverlay` 是 UObject 而非 Actor 或 ActorComponent，蓝图中通常通过以下方式使用：

1. **在其他 UObject/Component 中持有**：添加一个 `UPROPERTY()` 类型为 `UViewportWidgetOverlay*` 的成员
2. **在 Details 面板中配置**：设置 `WidgetClass` 为你的 UMG Widget 蓝图，选择各环境的 `DisplayType`
3. **在 Tick 中调用**：每帧调用 `Tick(DeltaTime)` 更新 Widget 状态
4. **控制显示/隐藏**：调用 `Display(World)` 显示，调用 `Hide()` 隐藏

## C++ 用法

### 头文件引入

```cpp
#include "ViewportWidgetOverlay.h"
```

### 基本用法

创建并配置一个 `UViewportWidgetOverlay` 实例，在 Tick 中更新，控制显示和隐藏：

```cpp
// 来源: Source/ViewportWidgetOverlay/Public/ViewportWidgetOverlay.h

// 创建实例
UViewportWidgetOverlay* Overlay = NewObject<UViewportWidgetOverlay>();

// 设置 Widget 类
Overlay->SetWidgetClass(MyWidgetClass);

// 配置各环境的显示方式
Overlay->SetDisplayTypes(
    EViewportWidgetOverlay_DisplayType::Viewport,                   // Editor
    EViewportWidgetOverlay_DisplayType::PostProcessSceneViewExtension, // Game
    EViewportWidgetOverlay_DisplayType::Viewport                     // PIE
);

// 显示 Widget
if (Overlay->ShouldDisplay(GetWorld()))
{
    Overlay->Display(GetWorld());
}

// 每帧更新（在 Tick 中调用）
Overlay->Tick(DeltaTime);

// 隐藏 Widget
Overlay->Hide();

// 检查当前是否正在显示
if (Overlay->IsDisplayed())
{
    // ...
}
```

### 进阶用法

#### 自定义后处理 Settings 来源

当使用 `PostProcessWithBlendMaterial` 模式时，可以指定一个自定义的 PostProcess Settings 对象（例如 VCam 中的 CineCamera 组件）：

```cpp
// 来源: Source/ViewportWidgetOverlay/Public/ViewportWidgetOverlay.h
// SetCustomPostProcessSettingsSource 文档注释

// 设置自定义 PostProcess Settings 来源（例如 CineCameraActor 的 PostProcessComponent）
Overlay->SetCustomPostProcessSettingsSource(MyCineCameraActor);
```

#### 配置后处理渲染参数

通过访问后处理显示类型设置来调整渲染参数：

```cpp
// 来源: Source/ViewportWidgetOverlay/Public/Misc/ViewportWidgetOverlay_PostProcessBase.h

// 获取 BlendMaterial 模式的后处理设置
FViewportWidgetOverlay_PostProcess& PPSettings = 
    Overlay->GetPostProcessDisplayTypeWithBlendMaterialSettings();

// 设置后处理材质
PPSettings.PostProcessMaterial = MyPostProcessMaterial;

// 设置色调和透明度
PPSettings.PostProcessTintColorAndOpacity = FLinearColor(1.0f, 1.0f, 1.0f, 0.8f);

// 设置纹理透明度
PPSettings.PostProcessOpacityFromTexture = 1.0f;

// 自定义渲染尺寸
PPSettings.bUseWidgetDrawSize = true;
PPSettings.WidgetDrawSize = FIntPoint(1920, 1080);

// 配置硬件输入接收
PPSettings.bReceiveHardwareInput = true;
```

#### Scene View Extension 模式的活跃条件

对于 `PostProcessSceneViewExtension` 模式，可以注册自定义的活跃条件 functor：

```cpp
// 来源: Source/ViewportWidgetOverlay/Public/Misc/ViewportWidgetOverlay_PostProcessWithSVE.h

FViewportWidgetOverlay_PostProcessWithSVE& SVESettings = 
    Overlay->GetPostProcessDisplayTypeWithSceneViewExtensionsSettings();

// 注册一个 functor 来控制 SVE 是否在当前帧生效
SVESettings.RegisterIsActiveFunctor(
    FSceneViewExtensionIsActiveFunctor::CreateLambda([](const ISceneViewExtension* Extension, const FSceneViewExtensionContext& Context)
    {
        // 返回空 optional 表示正常渲染，返回 false 表示跳过
        return TOptional<bool>(); 
    })
);
```

#### 编辑器中指定目标视口

```cpp
// 来源: Source/ViewportWidgetOverlay/Public/ViewportWidgetOverlay.h

#if WITH_EDITOR
// 设置目标视口（默认使用 GetFirstActiveLevelViewport）
Overlay->SetEditorTargetViewport(MySceneViewport);

// 重置为默认视口
Overlay->ResetEditorTargetViewport();
#endif
```

## Demo 示例

### 头文件

```cpp
// MyViewportOverlayComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MyViewportOverlayComponent.generated.h"

class UUserWidget;
class UViewportWidgetOverlay;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyViewportOverlayComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyViewportOverlayComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, 
                                FActorComponentTickFunction* ThisTickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 显示覆盖 Widget */
    UFUNCTION(BlueprintCallable)
    void ShowOverlay();

    /** 隐藏覆盖 Widget */
    UFUNCTION(BlueprintCallable)
    void HideOverlay();

    /** Widget 是否正在显示 */
    UFUNCTION(BlueprintPure)
    bool IsOverlayDisplayed() const;

protected:
    /** 要显示的 Widget 类 */
    UPROPERTY(EditAnywhere, Category = "Overlay")
    TSubclassOf<UUserWidget> WidgetClass;

    /** 编辑器显示模式 */
    UPROPERTY(EditAnywhere, Category = "Overlay")
    EViewportWidgetOverlay_DisplayType EditorDisplayType = EViewportWidgetOverlay_DisplayType::Viewport;

    /** 游戏显示模式 */
    UPROPERTY(EditAnywhere, Category = "Overlay")
    EViewportWidgetOverlay_DisplayType GameDisplayType = EViewportWidgetOverlay_DisplayType::PostProcessSceneViewExtension;

private:
    UPROPERTY()
    TObjectPtr<UViewportWidgetOverlay> ViewportOverlay;
};
```

### 源文件

```cpp
// MyViewportOverlayComponent.cpp
#include "MyViewportOverlayComponent.h"
#include "ViewportWidgetOverlay.h"

UMyViewportOverlayComponent::UMyViewportOverlayComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyViewportOverlayComponent::BeginPlay()
{
    Super::BeginPlay();

    ViewportOverlay = NewObject<UViewportWidgetOverlay>(this);
    ViewportOverlay->SetWidgetClass(WidgetClass);
    ViewportOverlay->SetDisplayTypes(
        EditorDisplayType,
        GameDisplayType,
        EViewportWidgetOverlay_DisplayType::Viewport  // PIE 默认用 Viewport 模式
    );
}

void UMyViewportOverlayComponent::TickComponent(float DeltaTime, ELevelTick TickType,
                                                  FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (ViewportOverlay)
    {
        ViewportOverlay->Tick(DeltaTime);
    }
}

void UMyViewportOverlayComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ViewportOverlay)
    {
        ViewportOverlay->Hide();
    }
    Super::EndPlay(EndPlayReason);
}

void UMyViewportOverlayComponent::ShowOverlay()
{
    if (ViewportOverlay && !ViewportOverlay->IsDisplayed())
    {
        ViewportOverlay->Display(GetWorld());
    }
}

void UMyViewportOverlayComponent::HideOverlay()
{
    if (ViewportOverlay)
    {
        ViewportOverlay->Hide();
    }
}

bool UMyViewportOverlayComponent::IsOverlayDisplayed() const
{
    return ViewportOverlay && ViewportOverlay->IsDisplayed();
}
```

## 模块依赖

> Build.cs 原文未提供，以下基于源码头文件引用推断。

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件为 Runtime 模块，LoadingPhase 为 `PostConfigInit`（因为需要在早期注册 Shader 目录映射），对依赖方无额外模块要求。使用者只需确保插件已启用即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-13 | `1d2f60e5` | [Rendering] Add missing includes and forward declarations for SceneView and rendering headers to fix compile errors. | 修复 SceneView 和渲染头文件缺失导致的编译错误 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将 UVPFullScreenWidget 从实验性 VPUtilities 插件迁移到独立的 ViewportWidgetOverlay 插件 |

### 维护评价

该插件创建于 2026 年 3 月，是一个非常新的插件。它从实验性的 VPUtilities 插件中提取出来，使全屏 Widget 覆盖功能独立可用。自创建以来已有 3 次提交，包括初始迁移、编译修复和日志宏更新，属于正常的工程迭代。

- **成熟度**：该插件源自成熟的 VPFullScreenWidget 实现，功能经过长期验证
- **维护状态**：活跃维护中，作为 Virtual Production 工作流的基础组件
- **已知限制**：`Composure` 显示模式已在 5.7 中废弃，不再受支持
- **推荐使用**：✅ 如果你需要在视口上覆盖 Widget（尤其是 VP/VCam/Pixel Streaming 场景），这是官方推荐的独立方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ViewportWidgetOverlay)
- 官方文档（无）