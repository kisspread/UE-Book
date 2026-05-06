# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇幻彩设备 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资源） |
| 模块 | `RazerChromaDevices` (Runtime), `RazerChromaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices) | |

## 用途

该插件封装了雷蛇 Chroma SDK，允许游戏在运行时动态控制雷蛇外设（如键盘、鼠标、耳机等）的 RGB 灯效。开发者可以利用它实现诸如血条变化、技能冷却、击杀反馈等场景下的灯光联动，增强游戏的沉浸感和外设沉浸体验。

## 使用场景

- 制作支持灯效联动的竞技游戏，根据玩家状态（连杀、血量、技能等）改变键盘或鼠标颜色。
- 在游戏中提供自定义灯效设置，允许玩家选择预设或创建自己的灯光方案。
- 用于开发调试工具，在编辑器内预览或测试灯效。
- 需要为雷蛇外设提供额外视觉反馈的任意项目。

## 蓝图用法

> 注意：该插件为实验性，蓝图函数库可能随版本变化。以下节点基于常见模式推测，实际 API 请以源码为准。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize Razer Chroma` | 初始化与雷蛇 Chroma 服务的连接 | `URazerChromaDevicesSubsystem` (推测) |
| `Set Static Color` | 将指定设备设置为纯色 | 同上 |
| `Set Wave Effect` | 播放波浪灯效 | 同上 |
| `Set Breathing Effect` | 设置呼吸灯效（单色/双色/随机） | 同上 |
| `Set Custom Effect` | 通过 2D 颜色数组自定义每个按键/区域的颜色 | 同上 |
| `Is Device Connected` | 检查指定设备是否已连接 | 同上 |

> 实际蓝图中，通常需要先调用“Initialize”节点，再调用具体灯效节点。建议在游戏开始时初始化一次。

### 使用示例（蓝图描述）

1. 在关卡蓝图或游戏实例中，拖出“Initialize Razer Chroma”节点，连接至事件“BeginPlay”。
2. 成功返回后，使用“Set Static Color”节点，选择设备类型（例如键盘、鼠标），设置颜色（RGB）。
3. 为灯效添加时间控制（例如使用 Timeline 或 Delay 节点）实现动态变化。

## C++ 用法

### 头文件引入

```cpp
#include "RazerChromaDevicesSubsystem.h"   // 假设子系统头文件
#include "RazerChromaSDK/RzChromaSDKDefines.h"  // 若需直接使用 SDK 类型
```

### 基本用法

```cpp
// 在任意模块（如 GameInstance 或 Character）中获取子系统
URazerChromaDevicesSubsystem* ChromaSubsystem = GEngine->GetEngineSubsystem<URazerChromaDevicesSubsystem>();
if (ChromaSubsystem && ChromaSubsystem->Initialize())
{
    // 设置键盘为纯红色
    ChromaSubsystem->SetStaticColor(ChromaSDK::BLACKWIDOW_CHROMA, FColor::Red);
}
```

**来源**：该示例基于典型子系统模式，实际代码路径：`Source/RazerChromaDevices/Public/`（未提供具体文件）。

### 进阶用法

```cpp
// 设置自定义灯效（键盘 30×30 矩阵）
ChromaSDK::CUSTOM_EFFECT_TYPE CustomEffect;
CustomEffect.Size = sizeof(CustomEffect);
for (int Row = 0; Row < ChromaSDK::MAX_ROW; ++Row)
    for (int Col = 0; Col < ChromaSDK::MAX_COLUMN; ++Col)
        CustomEffect.Color[Row][Col] = (Row + Col) % 2 ? 0x00FF0000 : 0x000000FF; // 红蓝棋盘

ChromaSubsystem->SetCustomEffect(ChromaSDK::BLACKWIDOW_CHROMA, CustomEffect);
```

## Demo 示例

以下为一个最小化的游戏模块示例，在首帧设置键盘灯效为静态红色。

### RazerChromaDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RazerChromaDemo.generated.h"

UCLASS()
class ARazerChromaDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

### RazerChromaDemo.cpp

```cpp
#include "RazerChromaDemo.h"
#include "RazerChromaDevicesSubsystem.h" // 假设路径

void ARazerChromaDemo::BeginPlay()
{
    Super::BeginPlay();

    URazerChromaDevicesSubsystem* Subsystem = GEngine->GetEngineSubsystem<URazerChromaDevicesSubsystem>();
    if (Subsystem && Subsystem->Initialize())
    {
        // 设置雷蛇黑寡妇蜘蛛键盘为纯红色
        Subsystem->SetStaticColor(ChromaSDK::BLACKWIDOW_CHROMA, FColor::Red);
    }
}
```

## 模块依赖

### 插件模块依赖

| 模块 | 用途 |
|---|---|
| `RazerChromaSDK` | 第三方雷蛇 Chroma SDK 封装，提供底层设备通信 |

> 注意：使用 `RazerChromaDevices` 或 `RazerChromaEditor` 模块时，需确保 `RazerChromaSDK` 模块已正确包含（通常自动引用）。

### 你的项目依赖

若要在你的模块中使用该插件，需在 `Build.cs` 中添加：

```csharp
PrivateDependencyModuleNames.AddRange(new string[] { "RazerChromaDevices" });
```

插件自身依赖较少，无特殊外部库（除 RazerChromaSDK 外）。

## 维护状态

### 近期更新

- 2025-07-10 `9803c443` 为含有对应 `.gen.cpp` 文件的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`
- 2025-06-26 `ec900998` 同上，继续添加宏
- 2025-06-10 `570dd339` RazerChromaEditor: 将私有目录移动以符合标准模块布局
- 2025-05-29 `1b731fe6` 禁用 Windows Arm64 上的 RazerChromaDevices 模块
- 2025-05-23 `13b6ed9e` 移除 win32 情况

### 维护评价

- 该插件于 2025 年 5 月创建，属于全新实验性插件。
- 近期更新主要是代码格式、目录结构调整和平台兼容性修复，尚无实质性功能增加。
- 标记为 `IsBetaVersion=true`，且默认未启用，表明尚不稳定、可能 API 会变动。
- 当前仅支持 Windows（x64），不支持 Arm64 和 Win32。
- 建议仅用于尝鲜或验证概念，生产环境需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices)
- [官方文档](https://docs.unrealengine.com)（未提供具体文档 URL，请查阅官方文档站搜索“Razer Chroma”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices/Source)（测试文件可能位于子模块内，暂未公开）

---

> ⚠️ **注意**：由于该插件处于实验阶段，上述蓝图节点和 C++ 函数名称仅为合理推测，实际使用时请参考插件最新源码。