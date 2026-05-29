# DMX Fixtures

> DMX Light Fixtures Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | DMX 灯光设备 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DMXFixtures` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXFixtures) | |

## 用途

本插件提供了一套标准化的蓝图 Actor 和组件框架，用于在 Unreal Engine 虚拟制片环境中模拟和控制支持 DMX512 协议的灯光设备。它不仅仅是简单的 DMX 信号接收，而是封装了灯光设备的物理层次结构（底座、摇头、灯头）、光学属性（光束质量、颜色、强度）、以及高级的矩阵像素灯光控制。它解决了将专业影视灯光（如摇头灯、洗墙灯、LED矩阵面板）以高保真度集成到实时虚拟场景中的核心问题。

## 使用场景

- 你需要在虚拟场景中模拟真实的影视灯光设备（如 ARRI、Martin、Chauvet 等品牌的灯具），并使用 DMX 控制台控制它们。
- 你正在搭建一个虚拟制片（Virtual Production）场景，需要精确控制多台灯光的颜色、位置、强度、光束形状等参数。
- 你需要创建一个像素控制的 LED 矩阵墙或灯条，并用 DMX 信号驱动其显示内容。
- 你希望在蓝图中快速搭建灯光设备逻辑，而无需从零开始编写复杂的 DMX 解析和灯光物理计算代码。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeFixture` | 初始化灯具，关联镜头和光束的网格体组件。 | `ADMXFixtureActor` |
| `PushNormalizedValuesPerAttribute` | 向灯具推送归一化的 DMX 属性值（0.0-1.0）。这是接收 DMX 信号的核心入口。 | `ADMXFixtureActorBase` |
| `InterpolateDMXComponents` | 在 Tick 中调用，驱动所有子组件的平滑插值动画。 | `ADMXFixtureActorBase` |
| `UpdateSpotLightIntensity` | 根据光强上限、锥角等参数，自动更新聚光灯强度。 | `ADMXFixtureActor` |
| `SetLightIntensityMax` | 设置灯光的最大光强。 | `ADMXFixtureActor` |
| `SetLightDistanceMax` | 设置灯光的最大衰减距离。 | `ADMXFixtureActor` |
| `SetLightColorTemp` | 设置灯光的色温。 | `ADMXFixtureActor` |
| `SetSpotlightIntensityScale` | 设置聚光灯的强度缩放。 | `ADMXFixtureActor` |
| `SetPointlightIntensityScale` | 设置点光源的强度缩放。 | `ADMXFixtureActor` |
| `SetLightCastShadow` | 设置灯光是否投射阴影。 | `ADMXFixtureActor` |
| `PushFixtureMatrixCellData` | 为矩阵灯具推送单个像素（Cell）的颜色数据。 | `ADMXFixtureActorMatrix` |
| `InitializeMatrixFixture` | 初始化矩阵灯具，生成其内部网格和纹理。 | `ADMXFixtureActorMatrix` |
| `GetDMXInterpolatedValue` | 获取单通道/双通道组件的当前插值结果值。 | `UDMXFixtureComponentSingle` / `UDMXFixtureComponentDouble` |
| `GetDMXTargetValue` | 获取单通道/双通道组件的目标值（插值终点）。 | `UDMXFixtureComponentSingle` / `UDMXFixtureComponentDouble` |
| `SetValueNoInterp` (Event) | 蓝图实现事件，用于直接设置单通道组件的最终值（无插值时调用）。 | `UDMXFixtureComponentSingle` |
| `SetChannel1ValueNoInterp` / `SetChannel2ValueNoInterp` (Event) | 蓝图实现事件，用于直接设置双通道组件中两个通道的最终值。 | `UDMXFixtureComponentDouble` |
| `SetColorNoInterp` (Event) | 蓝图实现事件，用于直接设置颜色组件的颜色值（颜色通道不进行插值）。 | `UDMXFixtureComponentColor` |

### 使用示例（蓝图描述）

1.  **基本摇头灯搭建**:
    *   在场景中放置一个 `DMXFixtureActor`。
    *   在其细节面板中，设置 `Base`、`Yoke`、`Head` 为对应的静态网格体组件或场景组件。
    *   将 `SpotLight` 和 `PointLight` 组件配置到 `Head` 组件下。
    *   调用 `InitializeFixture` 节点，传入镜头和光束的静态网格体组件。
    *   在 DMX 接收回调中，获取归一化的属性值映射，调用 `PushNormalizedValuesPerAttribute` 将其推送给 Actor。
    *   在 Actor 的 `Event Tick` 中调用 `InterpolateDMXComponents`。

2.  **创建自定义灯光效果组件**:
    *   创建一个继承自 `UDMXFixtureComponentSingle` 或 `UDMXFixtureComponentDouble` 的新蓝图类。
    *   重写 `SetValueNoInterp` (单通道) 或 `SetChannel1ValueNoInterp` / `SetChannel2ValueNoInterp` (双通道) 事件。
    *   在事件中，使用 `GetDMXInterpolatedValue` 获取当前的插值结果（如强度值），并应用到灯光材质或粒子系统。
    *   将此组件作为子组件添加到你的 `DMXFixtureActor` 中。

3.  **控制矩阵灯具**:
    *   放置一个 `DMXFixtureActorMatrix`。
    *   设置 `MatrixWidth`, `MatrixHeight`, `MatrixDepth` 定义矩阵物理尺寸。
    *   调用 `InitializeMatrixFixture` 进行初始化。
    *   构建一个 `TArray<FDMXCell>` 数据结构，包含每个像素的行列索引和颜色信息。
    *   调用 `PushFixtureMatrixCellData` 一次性更新所有像素。

## C++ 用法

### 头文件引入

```cpp
#include "DMXFixtureActor.h"
#include "DMXFixtureActorMatrix.h"
#include "DMXFixtureComponentSingle.h"
#include "DMXFixtureComponentDouble.h"
#include "DMXFixtureComponentColor.h"
```

### 基本用法

创建一个自定义的单通道 DMX 灯光控制组件。 (来源: `DMXFixtureComponentSingle.h`)

```cpp
// MySingleChannelComponent.h
#pragma once
#include "DMXFixtureComponentSingle.h"
#include "MySingleChannelComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMySingleChannelComponent : public UDMXFixtureComponentSingle
{
    GENERATED_BODY()

public:
    UMySingleChannelComponent();

    // 重写蓝图实现事件，处理来自 DMX 的最终值
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent, Category = "DMX")
    void SetValueNoInterp(float NewValue);
};

// MySingleChannelComponent.cpp
#include "MySingleChannelComponent.h"

UMySingleChannelComponent::UMySingleChannelComponent()
{
    // 配置此组件负责的 DMX 通道属性名
    DMXChannel.Name = FDMXAttributeName(TEXT("Intensity"));
    // 设置值的范围，例如 0 到 100 代表 0% 到 100%
    DMXChannel.MinValue = 0.0f;
    DMXChannel.MaxValue = 100.0f;
}
```

### 进阶用法

在自定义 Actor 中组合使用多个组件来控制一个复杂灯光。 (来源: 多个头文件组合)

```cpp
// MyCustomLightActor.h
#pragma once
#include "DMXFixtureActor.h"
#include "MyCustomLightActor.generated.h"

UCLASS()
class MYPROJECT_API AMyCustomLightActor : public ADMXFixtureActor
{
    GENERATED_BODY()

public:
    AMyCustomLightActor();

    // 初始化时，你可以添加自定义的组件
    virtual void BeginPlay() override;

    // 示例：重写 PushNormalizedValuesPerAttribute 进行特殊处理
    virtual void PushNormalizedValuesPerAttribute(const FDMXNormalizedAttributeValueMap& ValuePerAttributeMap) override;

private:
    // 指向你自定义的颜色组件
    UPROPERTY()
    TObjectPtr<UDMXFixtureComponentColor> CustomColorComponent;
};

// MyCustomLightActor.cpp
#include "MyCustomLightActor.h"
#include "DMXFixtureComponentColor.h"

AMyCustomLightActor::AMyCustomLightActor()
{
    // 添加一个颜色组件实例
    CustomColorComponent = CreateDefaultSubobject<UDMXFixtureComponentColor>(TEXT("ColorComponent"));
    // 设置它负责的颜色通道
    CustomColorComponent->DMXChannel1 = FDMXAttributeName(TEXT("ColorAdd_R"));
    CustomColorComponent->DMXChannel2 = FDMXAttributeName(TEXT("ColorAdd_G"));
    CustomColorComponent->DMXChannel3 = FDMXAttributeName(TEXT("ColorAdd_B"));
    CustomColorComponent->DMXChannel4 = FDMXAttributeName(TEXT("ColorAdd_W")); // 可选
}

void AMyCustomLightActor::BeginPlay()
{
    Super::BeginPlay();
    // 确保组件被正确初始化
    if (CustomColorComponent)
    {
        CustomColorComponent->Initialize();
    }
}

void AMyCustomLightActor::PushNormalizedValuesPerAttribute(const FDMXNormalizedAttributeValueMap& ValuePerAttributeMap)
{
    // 先调用父类处理基本灯光参数（Pan, Tilt, Dimmer等）
    Super::PushNormalizedValuesPerAttribute(ValuePerAttributeMap);

    // 你可以在这里添加额外的逻辑，例如基于特定属性值触发事件
    if (const float* GoboSpin = ValuePerAttributeMap.Map.Find(FDMXAttributeName(TEXT("Gobo_Spin"))))
    {
        // 处理 Gobo 旋转逻辑...
    }
}
```

## Demo 示例

一个最小的自定义 DMX 灯光控制组件示例。

```cpp
// DmxBasicComponent.h
#pragma once
#include "DMXFixtureComponentSingle.h"
#include "DmxBasicComponent.generated.h"

/**
 * 一个最基本的自定义 DMX 组件示例，负责将 DMX 强度值输出到日志。
 */
UCLASS(ClassGroup=(DMX), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UDmxBasicComponent : public UDMXFixtureComponentSingle
{
    GENERATED_BODY()

public:
    UDmxBasicComponent();

    /** 当收到新的 DMX 值且无需插值时，此函数被调用 */
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent, Category = "DMX Demo")
    void SetValueNoInterp(float NewValue);

protected:
    // 初始化组件
    virtual void Initialize() override;
};

// DmxBasicComponent.cpp
#include "DmxBasicComponent.h"
#include "DMXFixtureComponent.h" // for FDMXChannelData

UDmxBasicComponent::UDmxBasicComponent()
{
    // 定义此组件监听的 DMX 属性
    DMXChannel.Name = FDMXAttributeName(TEXT("Dimmer"));
    DMXChannel.MinValue = 0.0f;
    DMXChannel.MaxValue = 1.0f;
    DMXChannel.DefaultValue = 0.0f;

    // 启用插值，使值变化更平滑
    bUseInterpolation = true;
    InterpolationScale = 1.0f;
}

void UDmxBasicComponent::Initialize()
{
    Super::Initialize();
    UE_LOG(LogTemp, Log, TEXT("DmxBasicComponent Initialized for channel: %s"), *DMXChannel.Name.ToString());
}

// 为了演示，这里提供一个简单的蓝图实现。
// 在实际蓝图子类中，你需要重写 SetValueNoInterp 事件。
// void UDmxBasicComponent::SetValueNoInterp_Implementation(float NewValue)
// {
//     UE_LOG(LogTemp, Log, TEXT("DmxBasicComponent Received Value: %f"), NewValue);
//     // 在这里将值应用到你的灯光材质参数或动画
// }
```

## 模块依赖

使用此插件时，你的模块 Build.cs 需要添加对以下模块的依赖：

| 模块 | 用途 |
|---|---|
| `DMXFixtures` | 本插件核心模块，提供所有 Actor 和组件的基类。 |
| `DMXEngine` | 提供 DMX 核心功能、通道映射和连接管理。 |
| `DMXProtocol` | 提供底层的 DMX 协议实现（Art-Net, sACN 等）。 |
| `ProceduralMeshComponent` | 用于动态生成矩阵灯具的网格体。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 `Base` 重命名为 `Default`，符合引擎新规范。 |
| 2025-10-06 | `98034862` | Don't call RHIUpdateTexture2D, use UpdateTexture2D on a command list. | 优化矩阵灯具纹理更新，使用命令列表以提高性能和线程安全性。 |
| 2025-06-23 | `ed12aec9` | DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate | 代码清理，移除不必要的 `FORCEINLINE`，改为标准 `inline`。 |
| 2024-02-16 | `531e7a42` | DMX - DMXFixtureComponentDouble now applies its value range correctly | 修复了双通道组件值范围应用不正确的 Bug。 |
| 2024-01-25 | `dbdd172e` | CIS fix. | 持续集成系统配置修复。 |

### 维护评价

DMXFixtures 插件处于**活跃维护**状态。
*   **创建时间**：约 5 年，属于成熟插件。
*   **更新频率**：近一年内有多次实质性更新，包括性能优化（纹理更新）、代码规范化和重要 Bug 修复（双通道组件）。
*   **维护状态**：代码库仍在持续改进，遵循引擎的编码规范和最佳实践。
*   **推荐**：**强烈推荐**用于虚拟制片项目。它是 Epic 官方提供的标准解决方案，与 Unreal Engine 的 DMX 和灯光系统深度集成，稳定且功能全面。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXFixtures)
- [官方文档]() (无)
- [测试用例]() (未提供)