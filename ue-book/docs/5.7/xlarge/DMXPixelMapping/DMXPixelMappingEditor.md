# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Editor), `DMXPixelMappingEditorWidgets` (Editor), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 插件是 Unreal Engine 虚拟制作工具集的核心组成部分，专门用于解决将物理世界中的 LED 像素条、LED 面板或任何形状的灯具阵列映射到虚拟场景中的问题。它允许灯光设计师和虚拟制作艺术家在引擎内直观地创建、编辑和驱动复杂的 DMX 像素布局，将来自 DMX 控制台或蓝图的信号精确地分配到成千上万个虚拟灯具上，从而实现对大型 LED 墙、建筑立面灯光或舞台灯光装置的实时、精确控制。

## 使用场景

- **虚拟制作 LED 墙控制**：在 LED Volume 拍摄中，将 DMX 信号映射到构成虚拟背景的 LED 面板上，实现与摄像机运动同步的动态背景。
- **大型灯光装置编程**：为演唱会、主题公园或建筑照明设计复杂的灯光效果，通过可视化布局工具管理数百甚至数千个灯具。
- **交互式灯光艺术**：创建响应音频、用户输入或其他游戏逻辑的交互式灯光装置。
- **预可视化与编程**：在演出前，于引擎内预先编程和测试复杂的灯光序列，无需连接物理设备。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create DMX Pixel Mapping` | 创建一个新的 DMX 像素映射资产。 | `UDMXPixelMappingSubsystem` |
| `Get All Pixel Mapping Components` | 获取指定像素映射资产中的所有组件。 | `UDMXPixelMappingSubsystem` |
| `Send DMX` | 向指定的像素映射组件发送 DMX 数据。 | `UDMXPixelMappingComponent` |
| `Set Color` | 设置像素映射组件的渲染颜色。 | `UDMXPixelMappingFixtureComponent` |
| `Set Position` | 设置像素映射组件在布局中的位置。 | `UDMXPixelMappingBaseComponent` |
| `Render` | 触发像素映射的渲染更新。 | `UDMXPixelMappingRendererComponent` |

### 使用示例（蓝图描述）

1.  **创建并初始化映射**：使用 `Create DMX Pixel Mapping` 节点创建一个新资产，然后通过 `Get All Pixel Mapping Components` 获取其根组件。
2.  **构建布局**：在蓝图中，通过 `Add Child` 节点向根组件添加 `Fixture`（单个灯具）或 `Matrix`（灯具矩阵）组件，并使用 `Set Position` 和 `Set Size` 节点在 2D 布局视图中排列它们。
3.  **绑定数据与渲染**：将 `Fixture` 组件的 `DMX Library` 属性关联到你的 DMX 设备配置文件。在事件图表中，使用 `Send DMX` 节点或直接设置 `Color` 属性来驱动灯具，最后调用 `Render` 节点将变化应用到视口或输出。

## C++ 用法

### 头文件引入

```cpp
#include "DMXPixelMapping.h"
#include "DMXPixelMappingComponent.h"
#include "DMXPixelMappingSubsystem.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个简单的像素映射组件并设置其属性。

```cpp
// 获取 DMX 像素映射子系统
UDMXPixelMappingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UDMXPixelMappingSubsystem>();
if (Subsystem)
{
    // 创建一个新的像素映射资产
    UDMXPixelMapping* PixelMapping = Subsystem->CreateDMXPixelMapping(TEXT("MyMapping"));
    
    // 获取根组件
    UDMXPixelMappingBaseComponent* RootComponent = PixelMapping->GetRootComponent();
    
    // 创建一个灯具组件并添加到根组件下
    UDMXPixelMappingFixtureComponent* Fixture = NewObject<UDMXPixelMappingFixtureComponent>(RootComponent);
    Fixture->SetPosition(FVector2D(100.f, 50.f));
    Fixture->SetSize(FVector2D(20.f, 20.f));
    RootComponent->AddChild(Fixture);
    
    // 设置灯具的 DMX 库和起始通道
    Fixture->SetDMXLibrary(MyDMXLibrary);
    Fixture->SetStartingChannel(1);
}
```

### 进阶用法

结合渲染器组件，可以实现程序化驱动像素映射。

```cpp
// 假设已经有一个 UDMXPixelMappingRendererComponent* RendererComponent;
// 在 Tick 或自定义函数中更新所有灯具的颜色
void UpdatePixelMappingColors(UDMXPixelMappingRendererComponent* Renderer, float Time)
{
    if (!Renderer) return;
    
    TArray<UDMXPixelMappingComponent*> Components;
    Renderer->GetDMXPixelMapping()->GetAllComponentsOfClass<UDMXPixelMappingFixtureComponent>(Components);
    
    for (UDMXPixelMappingComponent* Comp : Components)
    {
        if (UDMXPixelMappingFixtureComponent* Fixture = Cast<UDMXPixelMappingFixtureComponent>(Comp))
        {
            // 根据时间计算颜色
            FLinearColor Color = FLinearColor::MakeRedGreenBlueFromHSV(Time * 60.f, 1.f, 1.f);
            Fixture->SetColor(Color);
        }
    }
    
    // 触发渲染
    Renderer->Render();
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个包含单个灯具的 DMX 像素映射。

**MyDMXPixelMappingActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyDMXPixelMappingActor.generated.h"

class UDMXPixelMapping;
class UDMXPixelMappingRendererComponent;

UCLASS()
class AMyDMXPixelMappingActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDMXPixelMappingActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMX")
    UDMXPixelMappingRendererComponent* RendererComponent;

private:
    UPROPERTY()
    UDMXPixelMapping* PixelMappingAsset;
};
```

**MyDMXPixelMappingActor.cpp**
```cpp
#include "MyDMXPixelMappingActor.h"
#include "DMXPixelMapping.h"
#include "DMXPixelMappingSubsystem.h"
#include "DMXPixelMappingRendererComponent.h"
#include "DMXPixelMappingFixtureComponent.h"

AMyDMXPixelMappingActor::AMyDMXPixelMappingActor()
{
    PrimaryActorTick.bCanEverTick = true;
    
    RendererComponent = CreateDefaultSubobject<UDMXPixelMappingRendererComponent>(TEXT("DMXRenderer"));
    RootComponent = RendererComponent;
}

void AMyDMXPixelMappingActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 创建并初始化像素映射
    UDMXPixelMappingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UDMXPixelMappingSubsystem>();
    if (Subsystem)
    {
        PixelMappingAsset = Subsystem->CreateDMXPixelMapping(TEXT("DemoMapping"));
        
        // 创建一个灯具组件
        UDMXPixelMappingFixtureComponent* Fixture = NewObject<UDMXPixelMappingFixtureComponent>(PixelMappingAsset->GetRootComponent());
        Fixture->SetPosition(FVector2D(0.f, 0.f));
        Fixture->SetSize(FVector2D(100.f, 100.f));
        PixelMappingAsset->GetRootComponent()->AddChild(Fixture);
        
        // 将映射资产设置给渲染器
        RendererComponent->SetDMXPixelMapping(PixelMappingAsset);
    }
}

void AMyDMXPixelMappingActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 简单的颜色循环动画
    if (PixelMappingAsset)
    {
        TArray<UDMXPixelMappingComponent*> Components;
        PixelMappingAsset->GetAllComponentsOfClass<UDMXPixelMappingFixtureComponent>(Components);
        
        for (UDMXPixelMappingComponent* Comp : Components)
        {
            if (UDMXPixelMappingFixtureComponent* Fixture = Cast<UDMXPixelMappingFixtureComponent>(Comp))
            {
                float Time = GetWorld()->GetTimeSeconds();
                FLinearColor Color = FLinearColor::MakeRedGreenBlueFromHSV(FMath::Fmod(Time * 90.f, 360.f), 1.f, 1.f);
                Fixture->SetColor(Color);
            }
        }
        
        RendererComponent->Render();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 提供底层的 DMX 协议通信支持。 |
| `DMXRuntime` | 提供 DMX 运行时库、设备管理和信号处理的核心功能。 |
| `DMXBlueprintGraph` | 提供与 DMX 相关的蓝图节点和图表编辑支持。 |
| `MeshDescription` | 用于生成和操作用于渲染像素映射的网格数据。 |
| `RHI`, `RenderCore` | 提供底层的渲染硬件接口和核心渲染功能，用于将像素映射渲染到纹理或视口。 |

## 维护状态

### 近期更新

- 462ec4ed8231 Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and subsequently destroyed.
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
- 1a49d758cda4 Moved "Public/MaterialTypes.h" header file to "Public/Materials/MaterialParameters.h".

### 维护评价

该插件创建于 2020 年，已有约 5 年历史，属于虚拟制作领域的成熟工具。从最近的提交记录来看，维护活动主要集中在**代码质量改进和重构**（如修复编译警告、统一代码风格、调整头文件结构），而非新功能开发。这表明插件已进入一个相对稳定的维护阶段，核心功能已经完善。虽然最近没有功能性更新，但持续的代码清理工作表明它仍在 Epic 的维护范围内，没有被废弃的迹象。对于需要进行 DMX 像素映射的虚拟制作项目，**推荐使用**此插件，它是官方提供的标准解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dmx-pixel-mapping-in-unreal-engine/) (UE5 官方文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Tests) (如果存在)