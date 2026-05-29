# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 中文名 | DMX 像素映射 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板、蓝图资产） |
| 模块 | `DMXPixelMappingCore` (Runtime), `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 解决的核心问题是：**将纹理、材质或 UMG Widget 的像素颜色实时读取并转换为 DMX 协议数据，驱动 LED 像素灯带、矩阵灯具阵列等 DMX 设备**。

在虚拟制作和现场演出场景中，LED 墙、像素灯带、可寻址灯具阵列需要与视频内容同步。传统方式需要外部软件（如 MadMapper、Resolume）来完成像素到 DMX 的映射，而本插件将这一流程完全集成在 UE 内部，实现：

- 从纹理/材质/UMG Widget 读取像素颜色
- 通过组件树结构组织灯具布局
- 将颜色值转换为 DMX 属性值（支持多种色彩空间）
- 通过 DMX 输出端口发送到物理设备

该插件是 UE DMX 协议栈（DMX Engine、DMX Protocol、DMX Library）之上的一层高级抽象，专注于"视频像素 → DMX 灯具"的映射管线。

## 使用场景

- 你在搭建 LED 视墙或像素灯带的虚拟场景，需要将视频内容实时映射为 DMX 数据 → 用 DMXPixelMapping 的 Renderer + Matrix 组件
- 你有一组按网格排列的可寻址 DMX 灯具，需要将纹理的像素颜色逐个发送 → 用 FixtureGroup + FixtureGroupItem 组件
- 你需要将 3D MVR 规格文件中的灯具坐标自动布局到 2D 像素映射中 → 用 LayoutByMVR 布局脚本
- 你的灯具使用 CIE xyY 或 XYZ 色彩空间而非标准 RGB → 用对应的 ColorSpace 配置
- 你需要在 Unreal Editor 中可视化编辑灯具位置、大小和旋转 → 本插件提供完整的 Designer 视图

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Sending DMX` | 启动像素映射，开始每帧读取像素并发送 DMX | `ADMXPixelMappingActor` |
| `Stop Sending DMX` | 停止发送 DMX | `ADMXPixelMappingActor` |
| `Pause Sending DMX` | 暂停发送 DMX | `ADMXPixelMappingActor` |
| `Is Sending DMX` | 查询当前是否正在发送 DMX | `ADMXPixelMappingActor` |
| `Set Stop Mode` | 设置停止时的 DMX 复位模式（发送默认值/发送零/保持最后值） | `ADMXPixelMappingActor` |
| `Reset DMX` | 重置组件及其所有子组件的 DMX 通道 | `UDMXPixelMappingBaseComponent` |
| `Send DMX` | 发送当前组件及子组件的 DMX 数据 | `UDMXPixelMappingBaseComponent` |
| `Render` | 渲染组件及子组件 | `UDMXPixelMappingBaseComponent` |
| `Render And Send DMX` | 渲染并发送 DMX（一步完成） | `UDMXPixelMappingBaseComponent` |
| `Get DMX Pixel Mapping Subsystem` | 获取像素映射子系统实例 | `UDMXPixelMappingSubsystem` |
| `Get Renderer Component` | 按名称获取 Renderer 组件 | `UDMXPixelMappingSubsystem` |
| `Get Output DMX Component` | 按名称获取 OutputDMX 组件 | `UDMXPixelMappingSubsystem` |
| `Get Fixture Group Component` | 按名称获取 FixtureGroup 组件 | `UDMXPixelMappingSubsystem` |
| `Get Matrix Component` | 按名称获取 Matrix 组件 | `UDMXPixelMappingSubsystem` |
| `Get DMX Pixel Mapping` | 加载像素映射资产 | `UDMXPixelMappingSubsystem` |
| `Get Root Component` | 获取组件树的根组件 | `UDMXPixelMapping` |
| `Get Pixel Mapping Component Modulators` | 获取指定 Fixture Patch 的调制器列表 | `UDMXPixelMappingRendererComponent` |

### 使用示例（蓝图描述）

**基本使用流程**：

1. 在场景中放置一个 `ADMXPixelMappingActor`
2. 在 Actor 的属性面板中设置 `Pixel Mapping` 为你的 DMXPixelMapping 资产
3. 勾选 `Auto Activate` 使其自动启动
4. 如需在编辑器中预览，勾选 `Send DMX in Editor`
5. 在 Level Blueprint 中，可通过 `Start Sending DMX` / `Stop Sending DMX` 节点控制播放

**运行时动态控制**：

1. 获取 `DMXPixelMappingSubsystem` → `Get DMX Pixel Mapping Subsystem`
2. 调用 `Get Renderer Component` 获取指定名称的渲染器
3. 调用 `Get DMX Pixel Mapping` 加载资产
4. 通过资产的 `Get Root Component` 获取根组件，再遍历子组件

## C++ 用法

### 头文件引入

```cpp
#include "DMXPixelMapping.h"
#include "Components/DMXPixelMappingBaseComponent.h"
#include "Components/DMXPixelMappingRendererComponent.h"
#include "Components/DMXPixelMappingMatrixComponent.h"
#include "Components/DMXPixelMappingOutputDMXComponent.h"
#include "Components/DMXPixelMappingFixtureGroupComponent.h"
```

### 基本用法

从源码 `Public/DMXPixelMapping.h` 和 `Public/Components/DMXPixelMappingBaseComponent.h` 提取：

```cpp
// 创建或加载一个像素映射资产
UDMXPixelMapping* PixelMapping = LoadObject<UDMXPixelMapping>(nullptr, TEXT("/Game/DMX/MyPixelMapping"));

// 启动 DMX 发送
PixelMapping->StartSendingDMX();

// 查询状态
if (PixelMapping->IsSendingDMX() && !PixelMapping->IsPaused())
{
    // 正在发送
}

// 设置停止时的复位行为
PixelMapping->SetResetDMXMode(EDMXPixelMappingResetDMXMode::SendDefaultValues);

// 停止发送
PixelMapping->StopSendingDMX();

// 暂停/恢复
PixelMapping->PauseSendingDMX();
```

### 进阶用法

**遍历组件树**（来自 `Public/DMXPixelMapping.h` 和 `Public/Components/DMXPixelMappingBaseComponent.h`）：

```cpp
// 获取根组件
UDMXPixelMappingRootComponent* Root = PixelMapping->GetRootComponent();

// 递归遍历所有组件
PixelMapping->ForEachComponent([](UDMXPixelMappingBaseComponent* Component)
{
    UE_LOG(LogTemp, Log, TEXT("Component: %s"), *Component->GetUserName());
});

// 按类型遍历
TArray<UDMXPixelMappingRendererComponent*> Renderers;
PixelMapping->GetAllComponentsOfClass<UDMXPixelMappingRendererComponent>(Renderers);

// 按名称查找
UDMXPixelMappingBaseComponent* Found = PixelMapping->FindComponent(FName("MyComponent"));

// 在组件树中递归查找指定类型的父组件
UDMXPixelMappingRendererComponent* Renderer = 
    UDMXPixelMappingBaseComponent::GetFirstParentByClass<UDMXPixelMappingRendererComponent>(SomeComponent);
```

**使用子系统获取组件**（来自 `Public/Blueprint/DMXPixelMappingSubsystem.h`）：

```cpp
UDMXPixelMappingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UDMXPixelMappingSubsystem>();

// 加载像素映射资产
UDMXPixelMapping* PixelMapping = Subsystem->GetDMXPixelMapping(LoadedAsset);

// 获取渲染器组件
UDMXPixelMappingRendererComponent* Renderer = 
    Subsystem->GetRendererComponent(PixelMapping, FName("MyRenderer"));

// 获取矩阵组件
UDMXPixelMappingMatrixComponent* Matrix = 
    Subsystem->GetMatrixComponent(PixelMapping, FName("MyMatrix"));
```

**通过 Actor 使用**（来自 `Internal/DMXPixelMappingActor.h`）：

```cpp
// 在场景中生成像素映射 Actor
ADMXPixelMappingActor* PixelMappingActor = GetWorld()->SpawnActor<ADMXPixelMappingActor>();
PixelMappingActor->SetPixelMapping(MyPixelMappingAsset);
PixelMappingActor->StartSendingDMX();

// 控制播放
PixelMappingActor->PauseSendingDMX();
bool bSending = PixelMappingActor->IsSendingDMX();
```

**DMX 复位模式枚举**（来自 `Public/Components/DMXPixelMappingBaseComponent.h`）：

```cpp
// 发送默认值（通常是 fixture type 中定义的默认属性值）
PixelMapping->SetResetDMXMode(EDMXPixelMappingResetDMXMode::SendDefaultValues);

// 发送全零值
PixelMapping->SetResetDMXMode(EDMXPixelMappingResetDMXMode::SendZeroValues);

// 保持最后映射的值不变
PixelMapping->SetResetDMXMode(EDMXPixelMappingResetDMXMode::DoNotSendValues);
```

## Demo 示例

以下是一个最小的像素映射使用示例，在场景中放置一个 DMXPixelMappingActor 并控制 DMX 发送：

**DMXPixelMappingDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXPixelMappingDemo.generated.h"

class ADMXPixelMappingActor;
class UDMXPixelMapping;

UCLASS()
class ADMXPixelMappingDemo : public AActor
{
    GENERATED_BODY()

public:
    ADMXPixelMappingDemo();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 启动像素映射 DMX 发送 */
    UFUNCTION(BlueprintCallable, Category = "DMX Demo")
    void StartPixelMapping();

    /** 停止像素映射 DMX 发送 */
    UFUNCTION(BlueprintCallable, Category = "DMX Demo")
    void StopPixelMapping();

    /** 暂停像素映射 DMX 发送 */
    UFUNCTION(BlueprintCallable, Category = "DMX Demo")
    void PausePixelMapping();

    /** 是否正在发送 */
    UFUNCTION(BlueprintPure, Category = "DMX Demo")
    bool IsPixelMappingActive() const;

private:
    /** 像素映射 Actor 实例 */
    UPROPERTY(Transient)
    TObjectPtr<ADMXPixelMappingActor> PixelMappingActor;

    /** 像素映射资产引用 */
    UPROPERTY(EditAnywhere, Category = "DMX Demo")
    TSoftObjectPtr<UDMXPixelMapping> PixelMappingAsset;

    /** 停止时的复位模式 */
    UPROPERTY(EditAnywhere, Category = "DMX Demo")
    EDMXPixelMappingResetDMXMode ResetMode = EDMXPixelMappingResetDMXMode::SendDefaultValues;
};
```

**DMXPixelMappingDemo.cpp**

```cpp
#include "DMXPixelMappingDemo.h"

#include "DMXPixelMappingActor.h"
#include "DMXPixelMapping.h"
#include "Components/DMXPixelMappingRootComponent.h"
#include "Components/DMXPixelMappingRendererComponent.h"
#include "Components/DMXPixelMappingBaseComponent.h"

ADMXPixelMappingDemo::ADMXPixelMappingDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADMXPixelMappingDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!PixelMappingAsset.IsNull())
    {
        // 生成像素映射 Actor
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        PixelMappingActor = GetWorld()->SpawnActor<ADMXPixelMappingActor>(SpawnParams);

        if (PixelMappingActor)
        {
            // 加载并设置像素映射资产
            UDMXPixelMapping* LoadedAsset = PixelMappingAsset.LoadSynchronous();
            if (LoadedAsset)
            {
                PixelMappingActor->SetPixelMapping(LoadedAsset);

                // 配置复位模式
                PixelMappingActor->SetStopMode(ResetMode);

                // 遍历并打印组件树结构
                LoadedAsset->ForEachComponent([](UDMXPixelMappingBaseComponent* Component)
                {
                    UE_LOG(LogTemp, Log, TEXT("PixelMapping Component: %s (Prefix: %s)"),
                        *Component->GetUserName(),
                        *Component->GetNamePrefix().ToString());
                });

                // 查找所有渲染器组件
                TArray<UDMXPixelMappingRendererComponent*> Renderers;
                LoadedAsset->GetAllComponentsOfClass<UDMXPixelMappingRendererComponent>(Renderers);

                for (UDMXPixelMappingRendererComponent* Renderer : Renderers)
                {
                    UE_LOG(LogTemp, Log, TEXT("Renderer: %s, Brightness: %f"),
                        *Renderer->GetUserName(), Renderer->Brightness);
                }
            }
        }
    }
}

void ADMXPixelMappingDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (PixelMappingActor)
    {
        PixelMappingActor->StopSendingDMX();
        PixelMappingActor->Destroy();
        PixelMappingActor = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}

void ADMXPixelMappingDemo::StartPixelMapping()
{
    if (PixelMappingActor)
    {
        PixelMappingActor->StartSendingDMX();
    }
}

void ADMXPixelMappingDemo::StopPixelMapping()
{
    if (PixelMappingActor)
    {
        PixelMappingActor->StopSendingDMX();
    }
}

void ADMXPixelMappingDemo::PausePixelMapping()
{
    if (PixelMappingActor)
    {
        PixelMappingActor->PauseSendingDMX();
    }
}

bool ADMXPixelMappingDemo::IsPixelMappingActive() const
{
    if (PixelMappingActor)
    {
        return PixelMappingActor->IsSendingDMX();
    }
    return false;
}
```

## 模块依赖

本插件包含 6 个 Runtime 模块，依赖关系紧密。使用者通常依赖 `DMXPixelMappingRuntime` 模块。

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | DMX 协议栈基础，提供 DMX 端口和数据收发能力 |
| `DMXRuntime` | DMX 运行时，提供 FixturePatch、FixtureType、DMXLibrary 等核心数据类型 |
| `DMXBlueprintGraph` | DMX 蓝图节点图支持 |
| `ColorManagement` | 色彩空间管理（用于 RGB/CMY/xyY/XYZ 转换） |

无特殊依赖（仅标准 Core/Engine/Slate 等 + 上述 DMX 相关模块）。

## 组件层次结构

```
UDMXPixelMappingRootComponent          (根组件)
├── UDMXPixelMappingRendererComponent  (渲染器 - 读取纹理/材质/Widget)
│   ├── UDMXPixelMappingFixtureGroupComponent     (灯具组)
│   │   └── UDMXPixelMappingFixtureGroupItemComponent  (单个灯具，发送 DMX)
│   └── UDMXPixelMappingMatrixComponent           (矩阵组)
│       └── UDMXPixelMappingMatrixCellComponent   (矩阵单元格)
└── UDEPRECATED_DMXPixelMappingScreenComponent    (已废弃)
```

## 色彩空间

DMXPixelMappingRuntime 内置 4 种色彩空间实现：

| 色彩空间 | 说明 | 用途 |
|---|---|---|
| `UDMXPixelMappingColorSpace_RGBCMY` | RGB / CMY 色彩空间，支持 sRGB/Rec2020/P3DCI/P3D65/PLASA 输出 | 最常用，兼容大多数 LED 设备 |
| `UDMXPixelMappingColorSpace_xyY` | CIE 1931 xyY 色彩空间 | 专业舞台灯具，精确色坐标控制 |
| `UDMXPixelMappingColorSpace_XYZ` | CIE 1931 XYZ 色彩空间 | 科学级色彩管理 |
| `UDMXPixelMappingColorSpace` | 基类（抽象） | 自定义色彩空间扩展 |

### RGB/CMY 色彩空间特性

- **输出色域**：sRGB、Rec2020、P3DCI、P3D65、PLASA RGB
- **Gamma 校正**：线性 / 跟随输出色域 / 自定义
- **CMY 转换**：可将 RGB 通道转换为 Cyan/Magenta/Yellow
- **亮度通道**：从颜色计算 / 常数值 / 从 Alpha / 无

### xyY 色彩空间特性

- 支持自定义色域范围（许多硬件使用 0.8 而非标准 1.0）
- 可配置 x、y、Y（亮度）的 DMX 属性映射

## 布局脚本

布局脚本（`UDMXPixelMappingLayoutScript`）用于自动排列组件位置和大小：

| 布局脚本 | 说明 |
|---|---|
| `UDMXPixelMappingLayoutScript_GridLayout` | 网格布局，支持行列数、间距、对齐方式 |
| `UDMXPixelMappingLayoutScript_LayoutByMVR` | 根据 MVR 规格文件中的 3D 坐标自动布局，支持多种投影平面（XY/XZ/YZ 等） |

布局脚本通过 `BlueprintNativeEvent` 机制实现，可在蓝图中创建自定义布局逻辑。

## 调制器（Modulators）

调制器在 DMX 输出前对属性值进行变换：

| 调制器 | 说明 |
|---|---|
| `UDMXModulator_PixelMappingFrameDelay` | 帧延迟调制器，将信号延迟指定帧数后输出，适用于像素映射的常量帧率场景 |

调制器通过 `UDMXPixelMappingOutputDMXComponent::ModulatorClasses` 属性配置，支持数组组合使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5f2a2a90` | DMX - Fix a crash when pixel mapping has unpatched components and draws patch colors | 修复未配置 Fixture Patch 的组件绘制补丁颜色时的崩溃 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联/解除关联通知重构 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了 CL53913857 的改动 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联/解除关联通知重构 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的警告 |

### 维护评价

- **活跃维护**：最近 6 个月内有功能性更新（5f2a2a90 修复崩溃 bug）和编译修复
- **近期更新**：2026 年 5 月有多次提交，涉及 bug 修复、编译警告清理、代码重构
- **持续演进**：源码中可见大量 `UE_DEPRECATED(5.3)` / `UE_DEPRECATED(5.4)` / `UE_DEPRECATED(5.5)` 标记，表明插件在持续重构和现代化（如 ScreenComponent 在 5.5 废弃，ColorSpace 系统在 5.3 重构）
- **已知废弃项**：`DMXPixelMappingScreenComponent` 已标记 Deprecated（5.5），应改用 Fixture Patch 工作流；多个旧接口在 5.3 已废弃
- **推荐使用**：✅ 推荐。作为 UE 官方虚拟制作工具链的核心组件，该插件处于活跃维护状态，API 持续现代化，适合作为 DMX 像素映射的标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档]()（暂无）