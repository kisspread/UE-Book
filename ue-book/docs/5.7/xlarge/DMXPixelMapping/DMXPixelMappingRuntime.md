# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 是一个用于将纹理、材质或 UMG 控件的像素颜色映射到 DMX 通道的工具集。它解决了虚拟制作中 LED 灯带、像素条和灯具阵列的控制问题——无论这些设备的形状或尺寸如何。

核心工作流程：
1. **输入源**：从纹理（Texture）、材质（Material）或 UMG 控件（UserWidget）读取像素颜色
2. **颜色转换**：通过可配置的颜色空间（RGB/CMY、xyY、XYZ）将像素颜色转换为 DMX 属性值
3. **DMX 输出**：将转换后的值通过 DMX 协议发送到实际的 LED 灯具

该插件采用组件树架构，支持：
- **Fixture Group**：将多个灯具组织成组
- **Matrix**：处理二维网格排列的像素阵列（如 LED 墙）
- **Layout Script**：通过蓝图脚本自定义组件的布局算法
- **Color Space**：支持多种颜色空间转换，包括 gamma 校正

## 使用场景

- 你在做虚拟制作，需要控制 LED 墙/像素灯带 → 用 DMXPixelMapping
- 你需要将视频/纹理内容实时映射到物理 LED 灯具 → 用 DMXPixelMapping
- 你有不规则形状的 LED 装置需要精确控制每个像素 → 用 DMXPixelMapping 的 Matrix 组件
- 你需要自定义灯具的布局排列方式 → 用 Layout Script 系统
- 你需要将 RGB 颜色转换为 CMY 或其他颜色空间再发送 DMX → 用 Color Space 系统

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartSendingDMX` | 开始发送 DMX 数据 | `ADMXPixelMappingActor` |
| `StopSendingDMX` | 停止发送 DMX 数据 | `ADMXPixelMappingActor` |
| `PauseSendingDMX` | 暂停发送 DMX 数据 | `ADMXPixelMappingActor` |
| `IsSendingDMX` | 查询是否正在发送 DMX | `ADMXPixelMappingActor` |
| `SetStopMode` | 设置停止时的 DMX 重置模式 | `ADMXPixelMappingActor` |
| `GetDMXPixelMappingSubsystem_Pure` | 获取 Pixel Mapping 子系统（纯函数） | `UDMXPixelMappingSubsystem` |
| `GetDMXPixelMappingSubsystem_Callable` | 获取 Pixel Mapping 子系统（可调用） | `UDMXPixelMappingSubsystem` |
| `GetDMXPixelMapping` | 加载 Pixel Mapping 资产 | `UDMXPixelMappingSubsystem` |
| `GetRendererComponent` | 获取渲染器组件 | `UDMXPixelMappingSubsystem` |
| `GetOutputDMXComponent` | 获取 DMX 输出组件 | `UDMXPixelMappingSubsystem` |
| `GetFixtureGroupComponent` | 获取灯具组组件 | `UDMXPixelMappingSubsystem` |
| `GetMatrixComponent` | 获取矩阵组件 | `UDMXPixelMappingSubsystem` |
| `GetPixelMappingComponentModulators` | 获取组件的调制器 | `UDMXPixelMappingRendererComponent` |

### 使用示例（蓝图描述）

**基本使用流程**：

1. 在场景中放置 `ADMXPixelMappingActor`
2. 在 Actor 的 Details 面板中设置 `PixelMapping` 属性为你的 DMXPixelMapping 资产
3. 设置 `bAutoActivate = true` 让它自动开始发送
4. 或者在 BeginPlay 中调用 `StartSendingDMX`

**通过子系统访问组件**：

1. 使用 `GetDMXPixelMappingSubsystem_Pure` 获取子系统
2. 使用 `GetRendererComponent` 获取渲染器，传入 PixelMapping 资产和组件名称
3. 使用 `GetFixtureGroupComponent` 或 `GetMatrixComponent` 获取输出组件

**停止时的重置模式**：

- `SendDefaultValues`：发送灯具的默认值
- `SendZeroValues`：发送零值
- `DoNotSendValues`：保持最后的映射值

## C++ 用法

### 头文件引入

```cpp
#include "DMXPixelMapping.h"
#include "DMXPixelMappingActor.h"
#include "DMXPixelMappingSubsystem.h"
#include "Components/DMXPixelMappingRendererComponent.h"
#include "Components/DMXPixelMappingMatrixComponent.h"
#include "Components/DMXPixelMappingFixtureGroupComponent.h"
#include "ColorSpace/DMXPixelMappingColorSpace.h"
#include "LayoutScripts/DMXPixelMappingLayoutScript.h"
```

### 基本用法

**通过 Actor 控制 DMX 发送**：

```cpp
// 在场景中获取或创建 Pixel Mapping Actor
ADMXPixelMappingActor* PixelMappingActor = GetWorld()->SpawnActor<ADMXPixelMappingActor>();

// 设置 Pixel Mapping 资产
PixelMappingActor->SetPixelMapping(MyPixelMappingAsset);

// 开始发送 DMX
PixelMappingActor->StartSendingDMX();

// 检查是否正在发送
if (PixelMappingActor->IsSendingDMX())
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Mapping is sending DMX"));
}

// 设置停止模式
PixelMappingActor->SetStopMode(EDMXPixelMappingResetDMXMode::SendZeroValues);

// 停止发送
PixelMappingActor->StopSendingDMX();
```

**直接操作 UDMXPixelMapping 对象**：

```cpp
// 获取 Pixel Mapping 对象
UDMXPixelMapping* PixelMapping = MyPixelMappingAsset;

// 开始/停止发送
PixelMapping->StartSendingDMX();
PixelMapping->StopSendingDMX();
PixelMapping->PauseSendingDMX();

// 查询状态
bool bIsSending = PixelMapping->IsSendingDMX();
bool bIsPaused = PixelMapping->IsPaused();

// 设置重置模式
PixelMapping->SetResetDMXMode(EDMXPixelMappingResetDMXMode::SendDefaultValues);
```

### 进阶用法

**遍历组件树**：

```cpp
// 获取根组件
UDMXPixelMappingRootComponent* Root = PixelMapping->GetRootComponent();

// 查找特定组件
UDMXPixelMappingBaseComponent* FoundComponent = PixelMapping->FindComponent(FName("MyComponent"));

// 按类型查找组件
UDMXPixelMappingRendererComponent* Renderer = PixelMapping->FindComponentOfClass<UDMXPixelMappingRendererComponent>(FName("MyRenderer"));

// 遍历所有组件
PixelMapping->ForEachComponent([](UDMXPixelMappingBaseComponent* Component)
{
    UE_LOG(LogTemp, Log, TEXT("Found component: %s"), *Component->GetUserName());
});
```

**使用颜色空间转换**：

```cpp
// 创建 RGB/CMY 颜色空间
UDMXPixelMappingColorSpace_RGBCMY* RGBCMYColorSpace = NewObject<UDMXPixelMappingColorSpace_RGBCMY>();

// 配置输出颜色空间
RGBCMYColorSpace->PixelMappingOutputColorSpace = EDMXPixelMappingOutputColorSpace_RGBCMY::sRGB;
RGBCMYColorSpace->OutputGamma = EDMXPixelMappingGamma_RGBCMY::AsOutputColorSpace;

// 设置 RGBA 输入值
FLinearColor InputColor(1.0f, 0.5f, 0.0f, 1.0f);
RGBCMYColorSpace->SetRGBA(InputColor);

// 获取转换后的属性值
const TMap<FDMXAttributeName, float>& AttributeValues = RGBCMYColorSpace->GetAttributeNameToValueMap();
for (const auto& Pair : AttributeValues)
{
    UE_LOG(LogTemp, Log, TEXT("Attribute: %s, Value: %f"), *Pair.Key.ToString(), Pair.Value);
}
```

**使用 Layout Script**：

```cpp
// 创建自定义布局脚本
UCLASS()
class UMyLayoutScript : public UDMXPixelMappingLayoutScript
{
    GENERATED_BODY()

public:
    virtual void Layout_Implementation(const TArray<FDMXPixelMappingLayoutToken>& InTokens, 
                                       TArray<FDMXPixelMappingLayoutToken>& OutTokens) override
    {
        // 自定义布局逻辑
        for (int32 i = 0; i < InTokens.Num(); i++)
        {
            FDMXPixelMappingLayoutToken Token = InTokens[i];
            Token.PositionX = i * 100.0f; // 水平排列
            Token.PositionY = 0.0f;
            Token.SizeX = 50.0f;
            Token.SizeY = 50.0f;
            OutTokens.Add(Token);
        }
    }
};
```

## Demo 示例

### 自定义 Layout Script

```cpp
// MyGridLayoutScript.h
#pragma once

#include "LayoutScripts/DMXPixelMappingLayoutScript.h"
#include "MyGridLayoutScript.generated.h"

UCLASS(meta = (DisplayName = "Grid Layout"))
class UMyGridLayoutScript : public UDMXPixelMappingLayoutScript
{
    GENERATED_BODY()

public:
    UMyGridLayoutScript();

    virtual void Layout_Implementation(const TArray<FDMXPixelMappingLayoutToken>& InTokens, 
                                       TArray<FDMXPixelMappingLayoutToken>& OutTokens) override;

    /** 网格列数 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid Layout")
    int32 NumColumns = 4;

    /** 单元格间距 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid Layout")
    float CellSpacing = 10.0f;
};
```

```cpp
// MyGridLayoutScript.cpp
#include "MyGridLayoutScript.h"

UMyGridLayoutScript::UMyGridLayoutScript()
{
    NumColumns = 4;
    CellSpacing = 10.0f;
}

void UMyGridLayoutScript::Layout_Implementation(const TArray<FDMXPixelMappingLayoutToken>& InTokens, 
                                                 TArray<FDMXPixelMappingLayoutToken>& OutTokens)
{
    OutTokens.Reserve(InTokens.Num());

    for (int32 i = 0; i < InTokens.Num(); i++)
    {
        FDMXPixelMappingLayoutToken Token = InTokens[i];

        // 计算网格位置
        int32 Row = i / NumColumns;
        int32 Col = i % NumColumns;

        Token.PositionX = Col * (Token.SizeX + CellSpacing);
        Token.PositionY = Row * (Token.SizeY + CellSpacing);

        OutTokens.Add(Token);
    }
}
```

### 自定义颜色空间

```cpp
// MyCustomColorSpace.h
#pragma once

#include "ColorSpace/DMXPixelMappingColorSpace.h"
#include "MyCustomColorSpace.generated.h"

UCLASS(meta = (DisplayName = "Custom HSV"))
class UMyCustomColorSpace : public UDMXPixelMappingColorSpace
{
    GENERATED_BODY()

public:
    UMyCustomColorSpace();

    virtual void SetRGBA(const FLinearColor& InColor) override;

    UPROPERTY(EditAnywhere, Category = "HSV")
    FDMXAttributeName HueAttribute;

    UPROPERTY(EditAnywhere, Category = "HSV")
    FDMXAttributeName SaturationAttribute;

    UPROPERTY(EditAnywhere, Category = "HSV")
    FDMXAttributeName ValueAttribute;
};
```

```cpp
// MyCustomColorSpace.cpp
#include "MyCustomColorSpace.h"

UMyCustomColorSpace::UMyCustomColorSpace()
{
    HueAttribute = FDMXAttributeName("Hue");
    SaturationAttribute = FDMXAttributeName("Saturation");
    ValueAttribute = FDMXAttributeName("Value");
}

void UMyCustomColorSpace::SetRGBA(const FLinearColor& InColor)
{
    // 转换 RGB 到 HSV
    float H, S, V;
    InColor.RGBToHSV(H, S, V);

    // 设置 DMX 属性值（归一化到 0-1）
    SetAttributeValue(HueAttribute, H / 360.0f);
    SetAttributeValue(SaturationAttribute, S);
    SetAttributeValue(ValueAttribute, V);
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | DMX 协议核心，用于 DMX 数据传输 |
| `DMXRuntime` | DMX 运行时库，提供 Fixture Patch、DMX Library 等基础类型 |
| `ColorManagement` | 颜色空间管理，用于 RGB/xyY/XYZ 等颜色空间转换 |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

```
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
- 365a11c5b937 [UObject/General] - Cleanup code and convert to the new ConditionalPreload function - Fix a few thread-safety issue when resetting flags before preloading
- 49325b518bcd DMX: Fix DMXPixelMappingActor '#undef LOCTEXT_NAMESPACE' without a corresponding '#define LOCTEXT_NAMESPACE'
```

### 维护评价

- **创建时间**：2020-09-24，约 5 年历史
- **最近更新**：近期有代码清理和线程安全修复，表明仍在维护
- **维护状态**：活跃维护中
- **已知限制**：
  - `UDMXPixelMappingScreenComponent` 已在 5.5 中废弃，推荐使用基于 Fixture Patch 的工作流
  - 部分旧的渲染方法（如 `QueueDownsample`、`RenderWithInputAndSendDMX`）已废弃，推荐使用 `UDMXPixelMappingPixelMapRenderer`
- **推荐使用**：✅ 推荐。这是 Epic 官方维护的虚拟制作核心插件，功能完善，文档和示例丰富

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dmx-pixel-mapping-in-unreal-engine/)（UE 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Tests)