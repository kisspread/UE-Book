# Geometry Mask

> 

| 属性 | 值 |
|---|---|
| 中文名 | 几何遮罩 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryMask` (Runtime), `GeometryMaskEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/GeometryMask) | |

## 用途

GeometryMask 插件为 Unreal Engine 的虚拟制片（Virtual Production）流程提供了一套基于场景几何体生成遮罩（Mask）的系统。其核心功能是让场景中的静态网格或动态网格物体作为“画笔”，将它们的轮廓绘制到一张共享的渲染目标纹理上。其他后期处理材质或系统可以读取这张纹理作为遮罩，从而实现精确控制后期效果（如景深、调色、特效等）的作用区域。它解决了在复杂场景中手动创建或动画化遮罩的难题，实现了遮罩与场景几何体的自动关联。

## 使用场景

-   **虚拟制片中的精确后期效果控制**：在 LED 虚拟制片中，你需要一个后期处理效果（如特定区域的调色或模糊）只作用于背景板（LED 屏幕）上，而忽略前景的演员和道具。使用此插件，你可以将背景板几何体设为遮罩写入者，效果自然只作用于背景区域。
-   **基于几何体的遮罩动画**：你需要一个物体（如一个打开的门或移动的箱子）的轮廓来动态遮挡或显现某个后期效果（如透过门看到的神秘光晕）。使用此插件，遮罩会随物体移动自动更新。
-   **UI 或 HUD 元素与场景的遮罩交互**：需要在 UI 层下方显示一个仅在特定形状区域内可见的底层场景内容（如雷达小地图）。可以将 UI 元素作为遮罩写入者。

## 蓝图用法

GeometryMask 插件的蓝图功能主要围绕“画布（Canvas）”的创建、写入和读取展开。

### 核心节点

#### 画布管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Named Canvas` | 根据名称和所在关卡获取一个遮罩画布。如果不存在则创建。 | `UGeometryMaskWorldSubsystem` |
| `Get Canvas Names` | 获取当前世界中所有已注册的画布名称。 | `UGeometryMaskWorldSubsystem` |
| `Remove Without Writers` | 清理掉所有没有写入者的画布。 | `UGeometryMaskWorldSubsystem` |
| `Get Render Target` | 获取画布所绘制到的纹理渲染目标（2D 数组）。 | `UGeometryMaskCanvas` |
| `Get Render Target Slice Index` | 获取画布在渲染目标纹理数组中的切片索引。 | `UGeometryMaskCanvas` |

#### 写入遮罩 (Writer)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Canvas Name` | 设置写入组件所引用的画布名称。 | `UGeometryMaskWriteMeshComponent` |
| `Get Parameters` | 获取写入参数结构体，包含画布名、复合操作、优先级等。 | `UGeometryMaskWriteMeshComponent` |

#### 读取遮罩 (Reader)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Canvas Name` | 设置读取组件所引用的画布名称。 | `UGeometryMaskReadComponent` |
| `Get Parameters` | 获取读取参数结构体，包含画布名、颜色通道、是否反转。 | `UGeometryMaskReadComponent` |

### 使用示例（蓝图描述）

**场景：为一个静态网格体添加遮罩写入功能**

1.  在你的 Actor 上，添加一个 `GeometryMaskWriteMeshComponent`。
2.  在组件的细节面板中，找到“Mask”分类下的“Canvas Name”属性，输入一个唯一的名称，例如 `BackgroundMask`。
3.  确保该 Actor 或其子级拥有网格体组件（如 `StaticMeshComponent`）。
4.  该写入组件会自动读取同级的网格体几何数据，并将轮廓绘制到名为 `BackgroundMask` 的画布上。
5.  在后期处理材质中，使用 `SceneTexture` 节点，并选择 `PostProcessInput0`，同时在材质参数中传入由 `GeometryMaskReadComponent` 提供的 `Mask_Textures` (即 `Get Render Target` 的返回值) 和 `Mask_TextureIndexVector` (包含 `Get Render Target Slice Index`) 来采样遮罩。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryMaskCanvas.h"
#include "GeometryMaskWorldSubsystem.h"
#include "GeometryMaskWriteComponent.h"
#include "GeometryMaskReadComponent.h"
```

### 基本用法

以下代码展示如何在 C++ 中获取画布并配置读取参数。

```cpp
// 获取当前世界的 GeometryMask 子系统
UGeometryMaskWorldSubsystem* WorldSubsystem = GetWorld()->GetSubsystem<UGeometryMaskWorldSubsystem>();
if (WorldSubsystem)
{
    // 根据名称获取或创建一个画布
    UGeometryMaskCanvas* Canvas = WorldSubsystem->GetNamedCanvas(GetLevel(), FName("MyMaskCanvas"));
    if (Canvas)
    {
        // 获取画布的渲染目标，用于传递给材质
        UTextureRenderTarget2DArray* RenderTarget = Canvas->GetRenderTarget();
        int32 SliceIndex = Canvas->BP_GetRenderTargetSliceIndex();
        
        UE_LOG(LogTemp, Log, TEXT("Canvas '%s' uses SliceIndex: %d"), *Canvas->GetCanvasName().ToString(), SliceIndex);
    }
}
```

### 进阶用法

以下代码展示如何实现自定义的遮罩写入者接口。

```cpp
// 在你的 Actor 或 Component 中实现 IGeometryMaskWriteInterface
UCLASS()
class AMyMaskedActor : public AActor, public IGeometryMaskWriteInterface
{
    GENERATED_BODY()
public:
    // 保存写入参数
    UPROPERTY(EditAnywhere, Category = "Mask")
    FGeometryMaskWriteParameters WriteParameters;

    // 实现接口
    virtual const FGeometryMaskWriteParameters& GetParameters() const override { return WriteParameters; }
    virtual void SetParameters(FGeometryMaskWriteParameters& InParameters) override { WriteParameters = InParameters; }
    virtual FOnGeometryMaskSetCanvasNativeDelegate& OnSetCanvas() override { return OnSetCanvasDelegate; }
    
    // 核心绘制函数：使用 FCanvas 绘制你的形状
    virtual void DrawToCanvas(FCanvas* InCanvas) override
    {
        if (!InCanvas) return;
        
        // 示例：绘制一个白色填充的圆。坐标需要是屏幕空间。
        const FIntPoint Size(512, 512); // 假设画布大小
        const FVector2D Center = Size / 2.0;
        const float Radius = 100.0f;
        
        InCanvas->DrawTile(Center.X - Radius, Center.Y - Radius, 
                          Radius * 2, Radius * 2, 
                          0, 0, 1, 1, 
                          FLinearColor::White, nullptr); // 使用纯白颜色绘制形状
    }

private:
    FOnGeometryMaskSetCanvasNativeDelegate OnSetCanvasDelegate;
};
```

## Demo 示例

一个可编译的最小示例，演示如何创建一个可以被遮罩系统读取的 Actor。

**MyMaskReaderActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "GeometryMaskReadComponent.h"
#include "MyMaskReaderActor.generated.h"

UCLASS()
class AMyMaskReaderActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyMaskReaderActor();
    
    // 用于读取遮罩的组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mask")
    TObjectPtr<UGeometryMaskReadComponent> MaskReaderComponent;
    
    // 在材质实例中使用的遮罩纹理参数名称
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mask")
    FName MaskTextureParameterName = "MaskTexture";
};
```

**MyMaskReaderActor.cpp**
```cpp
#include "MyMaskReaderActor.h"
#include "Kismet/GameplayStatics.h"

AMyMaskReaderActor::AMyMaskReaderActor()
{
    PrimaryActorTick.bCanEverTick = true;
    
    MaskReaderComponent = CreateDefaultSubobject<UGeometryMaskReadComponent>(TEXT("MaskReader"));
    // 设置要读取的画布名称，需要与写入端一致
    MaskReaderComponent->SetParameters(FGeometryMaskReadParameters{TEXT("BackgroundMask")});
}
```

## 模块依赖

使用 GeometryMask 插件，你的模块需要依赖渲染相关的模块。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 核心渲染功能，如 FCanvas、FSceneView 等。 |
| `RHI` | 渲染硬件接口，用于纹理资源和命令列表。 |
| `Renderer` | 渲染器模块，用于后处理和场景视图扩展。 |
| `GeometryMask` | **必需**。GeometryMask 运行时模块本身。 |
| `GeometryMaskEditor` | 仅在需要编辑器集成或自定义编辑器功能时需要。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `11b5ce93` | Motion Design: clarified masking deprecation messages + exposed GetRenderTargetSliceIndex so that c... | 清理废弃 API 的提示信息，并公开 `GetRenderTargetSliceIndex` 接口以便材质参数获取切片索引。 |
| 2026-04-29 | `3b158778` | Motion Design: fixed issue where a mask input modifier primitives remains hidden even after removing | 修复了遮罩写入组件在移除后其关联的网格体在编辑器中仍然显示为隐藏状态的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 `UE_LOGF` 格式。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将进行的头文件清理之前，预先添加必要的 `#include`。 |
| 2026-03-16 | `386c6e0b` | Motion Design: added geometry mask writer to decouple masking logic from actor component. Mask Write... | 新增独立的 `FMaskWriter` 逻辑，将遮罩绘制逻辑从 Actor 组件中解耦，提高代码复用性。 |

### 维护评价

**活跃维护**。该插件于 2025 年 5 月创建，年龄约 1 年。从 git 历史看，近期（2026 年 4 月、5 月）仍有功能增强和 Bug 修复的提交，例如解耦写入逻辑、修复编辑器显示问题等，表明它处于积极的维护和迭代中。虽然存在一些标记为 5.8 版本的废弃 API（主要涉及旧的基于颜色通道的资源管理，已被基于纹理数组切片的新方案取代），但这是功能演进的正常过程。**推荐使用**，特别是对于虚拟制片项目。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/GeometryMask)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/GeometryMask) (待确认具体路径)