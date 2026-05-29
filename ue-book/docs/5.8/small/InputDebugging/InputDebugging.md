# Input Debugging

> Input debugging and visualization.

| 属性 | 值 |
|---|---|
| 中文名 | 输入调试 |
| 分类 | Input |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InputDebugging` (Runtime), `InputDebuggingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-05-19 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InputDebugging) | |

## 用途

这个插件为开发者提供了运行时输入设备的调试和可视化工具。它主要解决以下问题：

1. **触控输入可视化**：在屏幕上实时绘制触控点的位置和压力信息，帮助开发者调试触摸输入相关的问题。
2. **输入设备调试**：通过 HUD 和控制台命令查看当前连接的硬件输入设备信息，包括设备标识符和设备属性。
3. **硬件设备枚举**：列出平台上所有已知的 `FHardwareDeviceIdentifier`，以及当前已连接的设备列表。

**重要限制**：InputDebugging 模块在 Shipping 构建中被排除（`TargetConfigurationDenyList: ["Shipping"]`），仅用于开发和调试阶段。

## 使用场景

- 你在开发支持触摸输入的移动游戏或平板应用 → 开启 `Input.Debug.ShowTouches 1` 查看触控点
- 你需要调试游戏手柄或特殊输入设备的连接和识别问题 → 使用控制台命令列出设备
- 你在 HUD 上需要实时查看输入设备的属性信息 → 通过 `ShowDebug` 系统显示设备信息

## 蓝图用法

本插件主要通过控制台命令和 HUD 调试显示工作，没有暴露蓝图可调用的函数。

### 控制台命令

| 命令 | 说明 |
|---|---|
| `Input.Debug.ShowTouches 1` | 开启触控输入可视化，在屏幕上绘制触控点 |
| `Input.Debug.ShowTouches 0` | 关闭触控输入可视化 |

### HUD 调试显示

通过 `ShowDebug` 系统（如在控制台输入 `ShowDebug DeviceProperties` 或 `ShowDebug HardwareDevices`）可以在游戏 HUD 上显示输入设备的调试信息。

## C++ 用法

本插件的类均为 Private 实现，不直接对外暴露 API。主要的内部类结构如下：

### 核心类

| 类 | 说明 |
|---|---|
| `FInputDeviceDebugTools` | 注册控制台命令和 HUD 调试绘制回调，提供设备枚举和日志输出功能 |
| `FTouchInputVisualizer` | 实现 `IInputProcessor` 接口，捕获鼠标/触摸事件并在 Canvas 上绘制触控点可视化 |

### FInputDeviceDebugTools

继承自 `TSharedFromThis`，在构造时注册控制台命令，在析构时移除。核心功能：

```cpp
// 私有方法 - 通过控制台命令触发
void ListAllKnownHardwareDeviceIdentifier(const TArray<FString>& Args, UWorld* World);
void LogAllConnectedDevices(const TArray<FString>& Args, UWorld* World);

// HUD 回调 - 自动注册到 ShowDebug 系统
static void OnShowDebugInfo(AHUD* HUD, UCanvas* Canvas, const FDebugDisplayInfo& DisplayInfo, float& YL, float& YPos);
static void OnShowDebugDeviceProperties(UCanvas* Canvas);
static void OnShowDebugHardwareDevices(UCanvas* Canvas);
```

### FTouchInputVisualizer

实现 `IInputProcessor` 接口，在 Slate 应用程序级别拦截输入事件：

```cpp
class FTouchInputVisualizer : public IInputProcessor
{
    // 捕获鼠标/触摸事件
    virtual bool HandleMouseMoveEvent(FSlateApplication& SlateApp, const FPointerEvent& MouseEvent) override;
    virtual bool HandleMouseButtonDownEvent(FSlateApplication& SlateApp, const FPointerEvent& MouseEvent) override;
    virtual bool HandleMouseButtonUpEvent(FSlateApplication& SlateApp, const FPointerEvent& MouseEvent) override;
    
    // Canvas 绘制回调
    void OnDebugDraw(class UCanvas* Canvas);

    // 内部数据结构
    struct FDebugTouchPoint
    {
        FVector2D Center;
        float Pressure;
    };
    TMap<uint32, FDebugTouchPoint> DebugTouchPoints;
};
```

触控点通过 `TMap<uint32, FDebugTouchPoint>` 跟踪，key 为触控点 ID，value 包含中心坐标和压力值。

## Demo 示例

由于本插件的类均为 Private 实现且不对外暴露，没有可直接使用的公共 API 示例。使用方式为：

1. 确保项目未在 Shipping 配置下编译
2. 运行游戏后打开控制台（`~` 键）
3. 输入 `Input.Debug.ShowTouches 1` 查看触控输入可视化
4. 输入 `ShowDebug` 并选择相应的设备调试类别查看设备信息

## 模块依赖

本插件的模块依赖仅包含标准 Core/Engine/Slate 等常见模块，无特殊依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `ee8a6c98` | Fix touch input debug circle position in editor by offsetting the drawn circle by the game viewport | 修复编辑器中触控调试圆圈的绘制偏移问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前的查找替换错误 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配 FCoreDelegates API 变更，修复注册缺失问题 |

### 维护评价

**活跃维护中**。最近的提交集中在 API 适配（如 `FCoreDelegates` 接口变更、`UE_LOG` 迁移）和 bug 修复（编辑器中触控点位置偏移）。作为 Epic 官方维护的调试工具插件，它会随着引擎 API 变更而持续更新。

- ✅ 持续维护，最近一次更新在 2026 年 4 月
- ✅ 功能稳定，作为开发调试工具持续可用
- ⚠️ 仅在非 Shipping 构建中可用，不能用于最终发行版本
- ✅ 推荐在开发阶段使用，特别是涉及触摸输入调试时

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InputDebugging)
- [官方文档]()（无）