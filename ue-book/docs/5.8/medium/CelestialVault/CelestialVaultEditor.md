# CelestialVault

> A DaySequence implementation of a Celestial Vault for Earth using ephemeris

| 属性 | 值 |
|---|---|
| 中文名 | 天穹模拟 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `CelestialVault` (Runtime), `CelestialVaultEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CelestialVault) | |

## 用途

CelestialVault 是一个基于天文星历（ephemeris）数据的天穹模拟系统，用于在游戏中还原地球真实的天空表现。它与 UE5 的 DaySequence 系统集成，能够根据地理位置（经纬度）和时间精确计算太阳、月亮、深空星体的位置和运动。

核心解决的问题：
- **真实天文模拟**：不是简单的天空盒贴图旋转，而是基于真实的天文学算法计算天体位置
- **夏令时处理**：内置 DaylightSavings 支持，根据地理位置自动处理夏令时偏移
- **Topocentric 坐标**：采用站心坐标系（TopocentricVaultComponent），考虑观察者位置的视差效果
- **高动态范围适配**：针对极高亮度范围的天体（如太阳）调整了 EyeAdaptation 参数

插件处于 Beta 阶段，由 Epic Games 开发维护。

## 使用场景

- 你在制作开放世界游戏需要真实日出日落、月相变化 → 用 CelestialVault
- 你需要基于真实经纬度模拟特定地区的天空 → 用 CelestialVault
- 你在做天文教育或模拟应用需要精确的天体位置 → 用 CelestialVault
- 你需要与 DaySequence 系统配合实现时间驱动的天空变化 → 用 CelestialVault

## 蓝图用法

### 核心节点

以下为编辑器工具模块（CelestialVaultEditor）暴露的蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewportCursorInformation` | 获取鼠标光标下的视口信息（聚焦状态、屏幕坐标、世界位置和方向） | `UCelestialVaultEditorUtilities` |
| `ComputeTextureMeanLuminance` | 计算指定纹理的平均亮度值，用于 HDR 天穹亮度校准 | `UCelestialVaultEditorUtilities` |

### 使用示例（蓝图描述）

**获取视口光标信息**：

1. 在蓝图中调用 `GetViewportCursorInformation` 节点
2. 连接 4 个输出引脚：`Focused`（布尔，编辑器是否聚焦）、`ScreenLocation`（二维屏幕坐标）、`WorldLocation`（摄像机世界位置）、`WorldDirection`（摄像机世界方向）
3. 可用于在编辑器中实现鼠标点击天空体的交互功能

**计算纹理平均亮度**：

1. 引用一个 `UTexture2D`（如天空渐变纹理或日盘纹理）
2. 调用 `ComputeTextureMeanLuminance` 节点
3. 输出 `OutMean` 为平均亮度浮点值，可用于调整曝光或校准 HDR 天穹亮度

### 自定义属性面板

插件为 DaylightSavings 类型提供了自定义属性面板（Property Customization），在编辑器的 Detail 面板中会根据以下信息自动调整显示：
- **年份**（Year）
- **夏令时模式**（DaylightSavingsMode：None 等）
- **纬度**（Latitude）

当这些属性在同一个 UObject 上存在时，DaylightSavings 面板会自动读取并展示上下文相关信息。

## C++ 用法

### 头文件引入

```cpp
#include "CelestialVaultEditor.h"           // 编辑器模块
#include "CelestialVaultEditorUtilities.h"  // 编辑器工具函数
#include "EditorViewportCameraProvider.h"   // 编辑器视口摄像机提供者
#include "DaylightSavingsCustomization.h"   // 夏令时属性自定义
```

### 基本用法 - 获取视口摄像机信息

```cpp
#include "CelestialVaultEditorUtilities.h"

void MyFunction()
{
    bool bFocused = false;
    FVector2D ScreenLocation;
    FVector WorldLocation;
    FVector WorldDirection;
    
    // 获取当前鼠标位置下的视口信息
    UCelestialVaultEditorUtilities::GetViewportCursorInformation(
        bFocused, ScreenLocation, WorldLocation, WorldDirection);
    
    if (bFocused)
    {
        // 使用 WorldLocation 和 WorldDirection 进行射线检测等操作
        UE_LOG(LogTemp, Log, TEXT("Cursor at screen: %s"), *ScreenLocation.ToString());
    }
}
```

### 基本用法 - 计算纹理亮度

```cpp
#include "CelestialVaultEditorUtilities.h"

void AnalyzeSkyTexture(UTexture2D* SkyTexture)
{
    float MeanLuminance = 0.0f;
    bool bSuccess = UCelestialVaultEditorUtilities::ComputeTextureMeanLuminance(
        SkyTexture, MeanLuminance);
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Sky texture mean luminance: %f"), MeanLuminance);
    }
}
```

### 进阶用法 - 自定义夏令时属性面板

```cpp
#include "DaylightSavingsCustomization.h"

// FDaylightSavingsCustomization 实现了 IPropertyTypeCustomization 接口
// 通常在编辑器模块启动时注册，用于在 Detail 面板中自定义 DaylightSavings 结构体的显示

// 注册方式（在模块 StartupModule 中）：
// PropertyModule.RegisterCustomPropertyTypeLayout(
//     FDaylightSavings::StaticStruct()->GetFName(),
//     FOnGetPropertyTypeCustomizationInstance::CreateStatic(
//         &FDaylightSavingsCustomization::MakeInstance));
```

## Demo 示例

以下展示如何在自己的模块中集成 CelestialVault 的编辑器工具：

```cpp
// MySkyAnalysis.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MySkyAnalysis.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMySkyAnalysis : public UActorComponent
{
    GENERATED_BODY()

public:
    /** 分析指定纹理的平均亮度，用于校准天穹曝光 */
    UFUNCTION(BlueprintCallable, Category = "Sky Analysis")
    bool AnalyzeSkyBrightness(UTexture2D* Texture, float& OutBrightness);
};
```

```cpp
// MySkyAnalysis.cpp
#include "MySkyAnalysis.h"
#include "CelestialVaultEditorUtilities.h"

bool UMySkyAnalysis::AnalyzeSkyBrightness(UTexture2D* Texture, float& OutBrightness)
{
    if (!Texture)
    {
        return false;
    }
    return UCelestialVaultEditorUtilities::ComputeTextureMeanLuminance(Texture, OutBrightness);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DaySequence` | DaySequence 时间系统集成，提供时间驱动的天穹变化 |
| `ViewportCameraProvider` | 视口摄像机抽象接口，用于获取编辑器/运行时摄像机信息 |
| `PropertyEditor` | 属性面板自定义框架，用于 DaylightSavings 的 Detail 面板定制 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-30 | `8701bcf1` | Fix TopocentricVaultComponent attachment to use NorthOffsetComponent as parent | 修复站心天穹组件的附着关系，以 NorthOffsetComponent 为父组件 |
| 2026-04-29 | `b69b383a` | Fixed: The DeepSky now follows the observer to remove the parallax effect on Stars | 修复深空星体跟随观察者移动以消除恒星视差效果 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-04-10 | `8130162b` | Switched the Celestial Vault Plugin to Beta | 将天穹模拟插件切换为 Beta 状态 |

### 维护评价

- **创建时间**：2026-04-10，非常新的插件
- **更新频率**：创建一个月内有 5 次提交，属于活跃开发阶段
- **维护状态**：活跃维护中，持续修复 bug 和优化渲染效果
- **已知限制**：Beta 阶段，API 可能发生变化；目前仅支持地球天穹模型
- **推荐程度**：适合在 Beta 阶段开始集成测试，但生产环境使用需谨慎关注版本更新

⚠️ **Beta 警告**：该插件标记为 `IsBetaVersion = true`，API 和功能可能在后续版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CelestialVault)
- [官方文档]()（暂无）