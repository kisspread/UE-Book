# PIX on Windows GPU Capture Plugin

> PIX on Windows graphics debugger integration.

| 属性 | 值 |
|---|---|
| 分类 | Developer |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | PixWinPlugin (DeveloperTool) |
| 创建时间 | 2021-03-18 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PixWinPlugin) | |

## 用途

PixWinPlugin 将 Microsoft PIX 图形调试器集成到 Unreal Engine 中。PIX 是 Windows 平台上最强大的 GPU 性能分析和图形调试工具之一，本 plugin 让开发者无需离开编辑器即可触发 GPU 帧捕获，并自动将捕获文件在 PIX 中打开进行分析。

核心功能：
- 在编辑器视口工具栏添加一键捕获按钮
- 注册 `pix.GpuCaptureFrame` 控制台命令，可在任何时候触发帧捕获
- 通过 `IRenderCaptureProvider` 接口为引擎的渲染捕获框架提供 PIX 后端实现
- 通过 `IInputDeviceModule` 注入一个 dummy 输入设备，利用其 Tick 回调来管理捕获的开始/结束时序
- 捕获文件保存为 `.wpix` 格式到 `{Project}/Saved/PixCaptures/` 目录

**注意**：此插件仅在 Windows 平台可用，且仅在非 Shipping 配置下生效（依赖 `WinPixEventRuntime`）。进程必须从 PIX 启动或使用 `-attachPIX` 命令行参数才能加载 `WinPixGpuCapturer.dll`。

## 使用场景

- 你需要分析 GPU 性能瓶颈（draw call 耗时、shader 执行效率等）→ 使用本插件在编辑器中一键捕获帧，然后在 PIX 中深入分析
- 你需要调试渲染问题（像素着色异常、渲染顺序错误等）→ 捕获帧后在 PIX 中逐 draw call 检查渲染状态
- 你需要在 Play In Editor (PIE) 模式下捕获游戏帧 → 使用快捷键 `Alt+F12` 或控制台命令

## 蓝图用法

本插件不暴露任何蓝图节点。它是一个纯开发者工具，通过编辑器 UI 和控制台命令操作。

## C++ 用法

### 头文件引入

```cpp
#include "IPixWinPlugin.h"
```

### 基本用法

#### 检查插件是否可用

```cpp
// 检查 PixWinPlugin 模块是否已加载
if (IPixWinPlugin::IsAvailable())
{
    // 获取模块引用
    IPixWinPlugin& PixPlugin = IPixWinPlugin::Get();
}
```

#### 通过 IRenderCaptureProvider 接口触发捕获

PixWinPlugin 同时实现了 `IRenderCaptureProvider` 接口。引擎的渲染捕获框架会通过 Modular Features 发现并使用它：

```cpp
#include "IRenderCaptureProvider.h"

// 通过 Modular Features 获取所有注册的渲染捕获提供者
TArray<IRenderCaptureProvider*> CaptureProviders =
    IModularFeatures::Get().GetModularFeatureImplementations<IRenderCaptureProvider>(
        IRenderCaptureProvider::GetModularFeatureName());

// 触发帧捕获（会自动选择已注册的 PIX 提供者）
if (CaptureProviders.Num() > 0)
{
    CaptureProviders[0]->CaptureFrame(nullptr, 0, FString());
}
```

### 进阶用法

#### 使用 BeginCapture/EndCapture 精确控制捕获范围

如果需要在 RHI 命令列表层面精确控制捕获的起止点：

```cpp
// 在 RHI 命令列表上开始捕获
PixPlugin.BeginCapture(&RHICmdList, IRenderCaptureProvider::ECaptureFlags_Launch, TEXT("MyCapture"));

// ... 提交需要捕获的渲染命令 ...

// 结束捕获
PixPlugin.EndCapture(&RHICmdList);
```

来源：`PixWinPluginModule.cpp` 中 `BeginCapture` / `EndCapture` 实现。

#### 控制台命令

在编辑器控制台或游戏控制台中输入：

```
pix.GpuCaptureFrame
```

将捕获下一帧的 GPU 渲染命令。捕获文件保存到 `{Project}/Saved/PixCaptures/`。

## Demo 示例

本插件是开箱即用的编辑器工具，不需要编写额外代码。使用步骤：

1. 用 PIX 启动 Unreal Editor（或在启动参数中添加 `-attachPIX`）
2. 在编辑器视口工具栏找到 PIX 捕获按钮（小相机图标），或按 `Alt+F12`
3. 捕获的 `.wpix` 文件自动保存到 `{Project}/Saved/PixCaptures/`
4. 如果 PIX 未附加，捕获完成后会自动在 PIX 中打开文件

## 模块依赖

### 公开依赖（使用本插件时需要引用）

| 模块 | 用途 |
|---|---|
| `InputDevice` | 提供 `IInputDeviceModule` 接口，用于注入 dummy 输入设备获取 Tick |
| `RenderCore` | 渲染核心模块，提供渲染线程命令队列等基础设施 |

### 私有依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（GameViewportClient 等） |
| `InputCore` | 输入核心 |
| `Projects` | 插件管理（IPluginManager） |
| `RHI` | 渲染硬件接口 |
| `WinPixEventRuntime` | PIX 运行时库（非 Shipping 配置） |

### 编辑器额外依赖

| 模块 | 用途 |
|---|---|
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能 |
| `ToolMenus` | 视口工具栏扩展 |
| `EditorFramework` | 编辑器框架 |
| `MainFrame` | 主窗口 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-14 | `17d692d2` | Use a more specific timestamp in the PIX capture filename | 改进文件名时间戳精度，避免多次捕获文件被覆盖 |
| 2025-05-27 | `2bef474f` | Update the various GPU debugger extensions to only support the new toolbar | 适配 UE5 新版视口工具栏，移除旧工具栏支持 |
| 2025-05-09 | `4e69b0b9` | Convert the PixWIN and XcodeGPUDebugger buttons to the new viewport toolbar | 将捕获按钮迁移到新版视口工具栏系统 |

### 维护评价

- **创建时间**：2021-03-18，约 5 年历史
- **维护状态**：**活跃维护** — 2025 年有多次功能性更新，包括工具栏适配和文件名改进
- **代码规模**：小巧精炼（9 个源文件），职责清晰，无历史包袱
- **平台限制**：仅 Windows，仅非 Shipping 配置
- **推荐使用**：✅ 如果你在 Windows 上做 GPU 性能分析或图形调试，这是必装插件。它默认启用，开箱即用。PIX 是微软官方的 Windows GPU 调试工具，与 UE5 的集成非常完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PixWinPlugin)
- [Microsoft PIX 官方工具](https://aka.ms/pixdownload)
- [测试用例]：本插件无独立测试用例
