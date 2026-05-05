# RenderDoc Plugin

> RenderDoc graphics debugger/profiler integration.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ✅ true |
| 包含内容 | false |
| 模块 | RenderDocPlugin (DeveloperTool) |
| 创建时间 | 2017-04-11 |
| 年龄标签 | 👴 老古董(>5年，~9年) |
| 平台支持 | Win64, Linux |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/RenderDocPlugin) | |

## 用途

将 [RenderDoc](https://renderdoc.org/) 图形调试器集成到 Unreal Editor 中。RenderDoc 是业界最常用的 GPU 帧捕获与调试工具，能够逐 draw call 地分析渲染管线。这个 plugin 解决的核心问题是：**让开发者无需离开编辑器，就能一键触发 RenderDoc 帧捕获，并自动打开 RenderDoc GUI 查看结果**。

Plugin 通过实现 `IRenderCaptureProvider` 和 `IInputDeviceModule` 两个接口来工作。选择 `IInputDeviceModule` 而非普通 `IModuleInterface` 是因为需要响应引擎 Tick 事件来管理延迟捕获、多帧捕获等时序逻辑。插件在启动时动态加载 RenderDoc 的 DLL（通过 `FRenderDocPluginLoader`），获取 RenderDoc API 上下文，然后通过该 API 控制帧捕获的全流程。

## 使用场景

- 你在调试某个材质的渲染结果不对 → 用 RenderDoc 捕获该帧，逐 draw call 查看 shader 输入/输出
- 你需要分析某个 pass 的 GPU 性能瓶颈 → 用 RenderDoc 查看每个 draw call 的耗时和资源绑定
- 你想检查某个 Render Target 的中间结果 → 在 RenderDoc 中查看任意 texture/RT 的内容
- 你需要对比两帧渲染差异 → RenderDoc 支持多帧对比分析
- 你在开发自定义渲染功能 → 捕获帧后可以查看完整的渲染管线状态

## 编辑器用法

### 工具栏按钮

Plugin 启用后，编辑器的 **Viewport 工具栏**会出现一个 RenderDoc 图标按钮。点击即可捕获当前视口的下一帧并自动打开 RenderDoc GUI。

### 快捷键

插件会自动注入快捷键绑定：**Alt + F12** → 触发帧捕获并启动 RenderDoc。

### 控制台命令

| 命令 | 说明 |
|---|---|
| `renderdoc.CaptureFrame` | 捕获下一帧并打开 RenderDoc GUI |
| `renderdoc.CapturePIE NumFrames` | 启动 PIE 会话并从头捕获指定帧数（仅编辑器） |

## 设置项

Plugin 在 **Project Settings → Plugins → RenderDoc** 中暴露以下配置项（对应 `URenderDocPluginSettings`，继承自 `UDeveloperSettings`）：

### Frame Capture Settings

| 设置项 | 控制台变量 | 默认值 | 说明 |
|---|---|---|---|
| Capture all activity | `renderdoc.CaptureAllActivity` | 0 | 捕获所有视口和编辑器窗口的全部活动，而非仅当前视口 |
| Capture all call stacks | `renderdoc.CaptureCallstacks` | 1 | 为每个 API 调用捕获调用栈（便于在 RenderDoc 中定位代码） |
| Reference all resources | `renderdoc.ReferenceAllResources` | 0 | 包含所有渲染资源（即使未使用），会显著增大捕获文件 |
| Save all initial states | `renderdoc.SaveAllInitials` | 0 | 始终捕获所有资源的初始状态，会显著增大捕获文件 |
| Capture delay in seconds | `renderdoc.CaptureDelayInSeconds` | 1 | 延迟单位：1=秒，0=帧数 |
| Capture delay | `renderdoc.CaptureDelay` | 0 | 触发捕获前等待的时间/帧数 |
| Capture frame count | `renderdoc.CaptureFrameCount` | 1 | 捕获的帧数（>1 时隐式启用 CaptureAllActivity） |

### Advanced Settings

| 设置项 | 控制台变量 | 默认值 | 说明 |
|---|---|---|---|
| Auto attach on startup | `renderdoc.AutoAttach` | - | 启动时自动附加 RenderDoc（否则需要 `-AttachRenderDoc` 命令行参数） |
| Show help on startup | `renderdoc.ShowHelpOnStartup` | - | 启动时显示帮助窗口（需重启） |
| Use RenderDoc crash handler | `renderdoc.EnableCrashHandler` | - | 使用 RenderDoc 的崩溃处理器（仅在确认是 RenderDoc 导致崩溃时启用，需重启） |
| RenderDoc executable path | `renderdoc.BinaryPath` | - | 指定 RenderDoc 可执行文件路径（需重启） |

所有设置项都可通过控制台变量在运行时修改（除标注"需重启"的项目外）。

## C++ 用法

### 头文件引入

```cpp
#include "IRenderDocPlugin.h"
```

### 检查插件可用性

```cpp
// 检查 RenderDoc 插件是否已加载
if (IRenderDocPlugin::IsAvailable())
{
    // 可以安全使用
    IRenderDocPlugin& RenderDoc = IRenderDocPlugin::Get();
}
```

### 通过 IRenderCaptureProvider 编程式捕获

RenderDoc 插件注册为 `IRenderCaptureProvider` 的模块化特性（Modular Feature），其他模块可以通过该接口触发帧捕获，无需直接依赖 RenderDoc 插件模块：

```cpp
#include "IRenderCaptureProvider.h"

// 获取所有已注册的 Render Capture Provider
TArray<IRenderCaptureProvider*> Providers;
IModularFeatures::Get().GetModularFeatureImplementations<IRenderCaptureProvider>(
    IRenderCaptureProvider::GetModularFeatureName(), Providers);

if (Providers.Num() > 0)
{
    IRenderCaptureProvider* Provider = Providers[0];

    // 捕获指定视口的下一帧，捕获完成后自动打开 RenderDoc
    Provider->CaptureFrame(Viewport, IRenderCaptureProvider::ECaptureFlags_Launch, TEXT("MyCapture"));

    // 或者使用 Begin/End 方式精确控制捕获范围
    FRHICommandListImmediate& RHICmdList = FRHICommandListExecutor::GetImmediateCommandList();
    Provider->BeginCapture(&RHICmdList, 0, TEXT("ManualCapture"));
    // ... 在此期间执行你想要捕获的渲染命令 ...
    Provider->EndCapture(&RHICmdList);
}
```

### 控制台命令

```cpp
// 在代码或控制台中触发帧捕获
// 控制台: renderdoc.CaptureFrame
// C++:
GEngine->Exec(nullptr, TEXT("renderdoc.CaptureFrame"));

// PIE 捕获：启动 PIE 并从头捕获 5 帧
// 控制台: renderdoc.CapturePIE 5
```

### 程序化多帧捕获

通过控制台变量控制捕获参数后再触发：

```cpp
// 设置捕获延迟 2 秒，捕获 3 帧
IConsoleVariable* DelayVar = IConsoleManager::Get().FindConsoleVariable(TEXT("renderdoc.CaptureDelay"));
if (DelayVar) DelayVar->Set(2);

IConsoleVariable* DelayUnitVar = IConsoleManager::Get().FindConsoleVariable(TEXT("renderdoc.CaptureDelayInSeconds"));
if (DelayUnitVar) DelayUnitVar->Set(1);

IConsoleVariable* FrameCountVar = IConsoleManager::Get().FindConsoleVariable(TEXT("renderdoc.CaptureFrameCount"));
if (FrameCountVar) FrameCountVar->Set(3);

// 触发捕获
GEngine->Exec(nullptr, TEXT("renderdoc.CaptureFrame"));
```

## 捕获文件位置

捕获的 `.rdc` 文件保存在：

```
{项目目录}/Saved/RenderDocCaptures/{时间戳}/
```

## 模块依赖

从 `RenderDocPlugin.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统 |
| `DesktopPlatform` | 桌面平台抽象（文件对话框等） |
| `Projects` | Plugin/Module 管理 |
| `RenderCore` | 渲染核心（Draw Events 等） |
| `InputDevice` | 输入设备模块接口 |
| `RHI` | RHI 抽象层（获取原生设备指针） |
| `DeveloperSettings` | 开发者设置基类 |
| `RenderDoc`（第三方静态库） | RenderDoc API 头文件和加载器 |

编辑器额外依赖：`Slate`, `SlateCore`, `EditorFramework`, `UnrealEd`, `MainFrame`, `GameProjectGeneration`, `ToolMenus`

## 架构说明

```
FRenderDocPluginModule (IModuleInterface + IRenderCaptureProvider + IInputDeviceModule)
├── FRenderDocPluginLoader         ← 动态加载 renderdoc.dll，获取 API 上下文
├── FRenderDocFrameCapturer        ← 帧捕获的静态工具类（Begin/End/Save/Launch）
├── FRenderDocDummyInputDevice     ← 虚拟输入设备，仅用于获取 Tick 回调
├── FRenderDocPluginEditorExtension ← 编辑器扩展（工具栏按钮）
├── URenderDocPluginSettings       ← 设置项（UDeveloperSettings 子类）
└── SRenderDocPluginHelpWindow     ← 启动帮助窗口
```

**关键设计决策**：Plugin 实现 `IInputDeviceModule` 而非普通模块，是为了获得每帧 Tick 回调来管理延迟捕获和多帧捕获的状态机（pending → in-progress → completed）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-06-26 | `ec90099` | 为含 .gen.cpp 的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME（自动代码修复） |
| 2025-05-27 | `2bef474` | 更新 GPU 调试器扩展仅支持新工具栏 |
| 2025-05-14 | `d0aa854` | 修复程序化 RenderDoc 捕获随机崩溃的问题 |

### 维护评价

- **创建时间**：2017 年 4 月，约 9 年历史
- **最近更新**：2025 年 6 月有更新（~10个月前），属于**活跃维护**
- **维护者**：最初由 Fredrik Lindh (Temaran) 贡献，后由 Epic Games 维护
- **稳定性**：最近的修复（2025-05）解决了程序化捕获的崩溃问题，说明仍在积极修复 bug
- **推荐度**：✅ **强烈推荐**。RenderDoc 是 GPU 调试的事实标准工具，这个插件是连接 UE5 和 RenderDoc 的官方桥梁，功能完善且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/RenderDocPlugin)
- [RenderDoc 官方文档](https://renderdoc.org/docs/index.html)
- [RenderDoc GitHub](https://github.com/baldurk/renderdoc)
