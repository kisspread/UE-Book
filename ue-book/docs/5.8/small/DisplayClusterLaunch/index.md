# nDisplay Launch

> Launch local nDisplay nodes with ease.

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 启动器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（图标资产） |
| 模块 | `DisplayClusterLaunchEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-07 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DisplayClusterLaunch) | |

## 用途

这是一个 **nDisplay 集群节点的编辑器端快速启动工具**。在虚拟制片工作流中，nDisplay 负责将渲染画面分发到多个物理显示器上，组成沉浸式 LED 墙或 CAVE 系统。启动 nDisplay 节点通常需要手动配置命令行参数、Multi-User 会话、控制台变量等繁琐步骤。

本插件将这些步骤封装成**编辑器工具栏一键启动**：选择场景中的 nDisplay Root Actor，配置好要启动的节点，点击工具栏按钮即可批量启动所有本地节点进程。它还自动处理 Multi-User (Concert) 会话连接、Unreal Insights 集成、控制台变量预设等常见需求。

**为什么存在**：在 nDisplay 大规模部署前的本地开发调试阶段，美术和技术美术需要频繁地启动/停止 nDisplay 节点。如果没有这个插件，每次都需要打开 Switchboard 或手动执行命令行，效率低下。本插件将这一流程简化为工具栏点击操作。

## 使用场景

- 你在开发 LED Volume（LED Volume）虚拟制片项目 → 需要在编辑器中快速启动 nDisplay 节点进行预览
- 你有一个 Multi-User 协作环境 → 启动 nDisplay 节点时自动连接到 Concert 会话
- 你需要在 nDisplay 节点上应用特定的控制台变量（如分辨率、渲染设置） → 通过项目设置配置预设
- 你需要为每个 nDisplay 节点收集 Unreal Insights 性能数据 → 在启动时自动启用 trace

## 前提条件

1. **需要手动启用**：该插件默认禁用（`EnabledByDefault: false`），需在 Edit → Plugins 中启用
2. **需要场景中有 nDisplay Root Actor**：插件通过扫描当前关卡中的 `ADisplayClusterRootActor` 获取可用配置
3. **标记为 Beta**：`IsBetaVersion: true`，API 和功能可能变动

## 项目设置

启用插件后，可在 **Edit → Project Settings → Plugins → nDisplay Launch Settings** 中配置：

### 基本设置

| 设置 | 说明 |
|---|---|
| `Close Editor On Launch` | 启动节点时是否关闭编辑器以优化性能 |
| `Console Variables Preset` | 指定一个 `ConsoleVariablesAsset` 预设，启动时自动应用 |
| `Additional Console Variables` | 追加控制台变量（在预设之后执行，可覆盖预设值） |
| `Additional Console Commands` | 追加控制台命令（如 `stat unit`） |
| `Command Line Arguments` | 附加命令行参数（不需要前缀 `-`，自动添加） |

### Multi-User 设置

| 设置 | 说明 |
|---|---|
| `Connect To Multi User` | 启动时是否连接或创建 Multi-User 会话 |
| `Explicit Session Name` | 指定会话名称（留空则自动生成） |

### Unreal Insights 设置

| 设置 | 说明 |
|---|---|
| `Enable Unreal Insights` | 启动时是否启用 Unreal Insights |
| `Enable Stat Named Events` | 是否支持 Stat Named Events |
| `Explicit Trace File Save Directory` | Trace 文件保存路径（留空则连接 localhost） |

### 日志设置

| 设置 | 说明 |
|---|---|
| `Log FileName` | 日志文件名（留空则使用节点名，自动追加 `.log`） |
| `Logging` | 日志分类及详细级别数组（`FDisplayClusterLaunchLoggingConstruct`） |

## 蓝图用法

本插件主要通过编辑器工具栏交互，**不提供 BlueprintCallable 节点**。所有启动逻辑由模块内部私有方法驱动，对外仅暴露项目设置（`UDisplayClusterLaunchEditorProjectSettings`）。

### 工具栏交互

启用插件后，编辑器工具栏会出现 **nDisplay Launch** 按钮：

1. **选择配置**：点击下拉菜单，选择当前关卡中的 `ADisplayClusterRootActor`
2. **选择节点**：在下拉子菜单中勾选要启动的节点（主节点会标注）
3. **选择附加 ConsoleVariables 资产**（可选）
4. **点击启动**：调用 `TryLaunchDisplayClusterProcess()`

### 可用的公开接口

| 方法 | 说明 | 所在类 |
|---|---|---|
| `OpenProjectSettings()` | 打开 nDisplay Launch 项目设置页面 | `FDisplayClusterLaunchEditorModule` |
| `TryLaunchDisplayClusterProcess()` | 启动 nDisplay 节点流程（包含 Multi-User 和 ConsoleVariables 处理） | `FDisplayClusterLaunchEditorModule` |
| `TerminateActiveDisplayClusterProcesses()` | 终止所有已启动的 nDisplay 节点进程 | `FDisplayClusterLaunchEditorModule` |

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterLaunchEditorModule.h"
```

### 基本用法

```cpp
// 获取模块实例并启动 nDisplay 流程
FDisplayClusterLaunchEditorModule& LaunchModule = FDisplayClusterLaunchEditorModule::Get();
LaunchModule.TryLaunchDisplayClusterProcess();
```

### 打开项目设置

```cpp
// 在代码中直接跳转到 nDisplay Launch 项目设置
FDisplayClusterLaunchEditorModule::OpenProjectSettings();
```

### 终止所有节点进程

```cpp
// 终止所有已启动的 nDisplay 节点进程
FDisplayClusterLaunchEditorModule::Get().TerminateActiveDisplayClusterProcesses();
```

### 自定义项目设置（C++ 中读取）

```cpp
#include "DisplayClusterLaunchEditorProjectSettings.h"

const UDisplayClusterLaunchEditorProjectSettings* Settings = GetDefault<UDisplayClusterLaunchEditorProjectSettings>();

if (Settings->bConnectToMultiUser)
{
    // Multi-User 模式
    FString SessionName = Settings->ExplicitSessionName;
}

if (Settings->bEnableUnrealInsights)
{
    // Unreal Insights 已启用
    FDirectoryPath TraceDir = Settings->ExplicitTraceFileSaveDirectory;
}

// 获取附加控制台变量
for (const FString& CVar : Settings->AdditionalConsoleVariables)
{
    // 每个 CVar 格式如 "r.ScreenPercentage 50"
    UE_LOG(LogDisplayClusterLaunchEditor, Log, TEXT("附加 CVar: %s"), *CVar);
}
```

## 内部工作流程

插件启动 nDisplay 节点的核心流程如下：

```
TryLaunchDisplayClusterProcess()
    │
    ├── 检查当前关卡是否有 nDisplay Root Actor
    ├── 收集项目设置参数（命令行、CVar、日志等）
    │
    ├── [如果启用了 Multi-User]
    │   ├── EnsureMultiUserDiscovery()
    │   ├── FindOrLaunchConcertServer()
    │   ├── FindAppropriateServer()
    │   └── ConnectToSession()
    │
    └── LaunchDisplayClusterProcess()
        ├── 为每个选中的节点生成命令行
        ├── 应用 ConsoleVariables 预设
        ├── 应用附加命令行参数
        └── 创建子进程 (FProcHandle)
```

## 模块依赖

本插件的 Build.cs 未直接提供，但根据源码引用可推断以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心模块（`ADisplayClusterRootActor`、`UDisplayClusterConfigurationData`） |
| `Concert` / `ConcertSyncCore` | Multi-User 协作会话管理（`FConcertServerInfo`） |
| `ConsoleVariablesEditorRuntime` | 控制台变量资产（`ConsoleVariablesAsset`） |
| `ToolMenus` | 编辑器工具栏菜单注册 |
| `PlacementMode` | 放置面板集成 |

其余为标准依赖（Core、Engine、Slate、UMG 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为 UE_LOGF 格式 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式化说明符错误 |
| 2025-10-09 | `1d4d3982` | Specify the SupportedPlatformTargets in the DisplayClusterLaunch plugin to prevent it from getting i | 显式声明支持的平台目标以避免打包问题 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将 Base 配置文件重命名为 Default 命名规范 |
| 2025-09-03 | `65d9e8d9` | [nDisplay] Added few more CVars to the DisplayClusterLauncher launch command line | 在启动命令行中增加更多控制台变量支持 |

### 维护评价

- **创建时间**：2022-04-07，约 4 年历史
- **维护状态**：**活跃维护中**。2026 年仍有持续更新，修复编译问题和平台兼容性
- **更新特点**：近期更新以维护性修复为主（日志迁移、格式符修复、平台声明），无重大功能变更
- **Beta 状态**：插件仍标记为 `IsBetaVersion: true`，自创建以来一直是 Beta
- **推荐使用**：✅ 推荐用于虚拟制片本地 nDisplay 开发调试。虽然标记为 Beta，但 Epic Games 持续维护，稳定性可接受。**不建议在生产环境的自动部署流程中依赖此插件**，生产环境应使用 Switchboard 或自定义脚本

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/DisplayClusterLaunch)
- [nDisplay 官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/)
- [Switchboard 文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/Switchboard/)