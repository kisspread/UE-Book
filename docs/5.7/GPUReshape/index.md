# GPU Reshape Plugin

> GPU Reshape editor integration

| 属性 | 值 |
|---|---|
| 分类 | Developer (Folder) / Rendering (.uplugin Category) |
| 默认启用 | ✅ EnabledByDefault |
| 包含内容 | ❌ |
| 模块 | GPUReshape (DeveloperTool) |
| 加载阶段 | PostConfigInit |
| 支持平台 | Win64 |
| 创建时间 | 2025-05-19 |
| 年龄标签 | 🆕 (~1 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/GPUReshape) | |

## 用途

GPUReshape 是 Epic 为 [GPU-Reshape](https://github.com/GPUOpen-Effects/GPU-Reshape)（由 AMD / Fatalist Development AB 开发的 GPU 调试/检测工具）编写的 **UE5 编辑器集成插件**。

GPU-Reshape 是一个独立的桌面应用程序，能在运行时对 GPU 指令进行 **instrumentation（插桩）**，检测并报告以下问题：

- **资源状态错误**：未初始化的纹理读取、描述符越界等
- **并发竞争**：GPU 命令缓冲区之间的数据竞争
- **循环问题**：着色器中的死循环或边界条件
- **导出稳定性**：着色器导出的可靠性验证

该插件本身 **不做 GPU 检测**，它只是一个"启动器 + 注入器"：

1. 在模块启动时，加载 `GRS.Services.Loader.dll`，将 GPU-Reshape 的 DX12/Vulkan Layer 注入到当前进程
2. 在编辑器工具栏添加按钮，一键启动 GPU-Reshape 桌面应用并 attach 到当前编辑器进程
3. 通过 PID + Token 机制确保应用只连接到正确的编辑器实例

**简单来说**：如果你需要在 UE5 编辑器中检测 GPU 资源访问违规、着色器并发问题等底层 GPU bug，这个插件帮你快速接入 GPU-Reshape 工具链。

## 使用场景

- **GPU 验证调试**：你的渲染出现了花屏/黑块/闪烁等 GPU 层面的异常，需要检测是哪个 Draw Call / Shader 出了问题
- **描述符越界排查**：怀疑绑定的 UAV/SRV/CBV 索引越界，需要 GPU 层面的 bounds checking
- **未初始化资源检测**：需要检测哪些纹理/缓冲区在读取前没有被正确写入
- **着色器并发调试**：多 Pass 渲染中怀疑有资源竞争

> ⚠️ 仅支持 **Win64** 平台，不支持 Null RHI 和 Server target。

## 使用方法

### 方式一：命令行参数（推荐）

在启动 UE5 时通过命令行参数启用注入：

```bash
# 三选一，效果相同
UnrealEditor.exe -AttachGRS
UnrealEditor.exe -AttachReshape
UnrealEditor.exe -AttachGPUReshape
```

### 方式二：控制台变量

在 `DefaultEngine.ini` 中设置，或者在运行时通过控制台设置：

```ini
[/Script/Engine.RendererSettings]
r.AutoAttachGPUReshape=1
```

> 注意：该 CVar 标记了 `ECVF_ReadOnly`，修改后需要重启编辑器才生效。

### 方式三：编辑器工具栏按钮

插件成功初始化后，会在 **Viewport Toolbar（视口工具栏）** 左侧添加一个 GPU Reshape 图标按钮。点击即可打开 GPU-Reshape 应用。

### 打开 GPU-Reshape 应用

注入成功后，可以通过以下方式打开 GPU-Reshape 桌面应用：

| 方式 | 操作 |
|---|---|
| 快捷键 | `Alt + F12` |
| 控制台 | 输入 `GRS` 回车 |
| 工具栏 | 点击视口工具栏上的 GPU Reshape 图标 |

应用启动后会自动 attach 到当前编辑器进程（通过 PID + Token），如果应用已经在运行则会切换到前台。

### 自定义路径

如果 GPU-Reshape 的二进制文件不在默认位置，可以通过命令行参数覆盖：

```bash
# 指定自定义路径
UnrealEditor.exe -GRSPath="D:/Tools/GPUReshape/Binaries"

# 指定分支（默认为 Raytracing）
UnrealEditor.exe -GRSBranch=Dev
```

默认二进制路径为：`Engine/Binaries/ThirdParty/GPUReshape/Win64/{Branch}/`

## 蓝图用法

无。该插件不暴露任何蓝图接口，是纯编辑器工具集成。

## C++ 用法

该插件不设计为被其他模块 API 引用。它是自包含的编辑器集成，所有功能通过控制台命令和编辑器 UI 触发。

如果确实需要以编程方式检查插件状态：

```cpp
#include "GPUReshapeModule.h"

// 检查插件是否成功初始化
FGPUReshapeModule& Module = FModuleManager::GetModuleChecked<FGPUReshapeModule>("GPUReshape");
if (Module.IsInitialized())
{
    // GPU-Reshape 已注入，可以安全启动应用
    Module.OpenOrSwitchToApp();
}

// 获取应用进程 ID（如果正在运行）
uint32 ProcessID = Module.GetAppGetProcessID();
```

## 内部架构

```
GPUReshape Plugin
├── FGPUReshapeModule      ← 主模块：Loader 注入 + 应用管理
│   ├── FindAndInstallLoader()  ← 加载 GRS.Services.Loader.dll 并注入 Layer
│   ├── OpenOrSwitchToApp()     ← 启动/切换 GPUReshape.exe
│   └── CacheLoaderReservedToken() ← 获取 attach 用的 Token
├── FGPUReshapeCommands    ← 编辑器快捷键注册 (Alt+F12)
└── FGPUReshapeStyle       ← Slate 样式/图标注册
```

依赖的第三方二进制（`Engine/Binaries/ThirdParty/GPUReshape/Win64/Raytracing/`）：

| 组件 | 说明 |
|---|---|
| `GPUReshape.exe` | Avalonia (.NET) 桌面应用，GPU-Reshape 主 UI |
| `GRS.Services.Loader.dll` | 运行时注入器，处理 Layer 注入 |
| `GRS.Backends.DX12.Layer.dll` | DX12 后端拦截层 |
| `GRS.Backends.DX12.Discovery.dll` | DX12 设备发现 |
| `GRS.Backends.Vulkan.Discovery.dll` | Vulkan 设备发现 |
| `GRS.Features.Descriptor.Backend.dll` | 描述符验证特性 |
| `GRS.Features.Concurrency.Backend.dll` | 并发检测特性 |
| `GRS.Features.Loop.Backend.dll` | 循环检测特性 |
| `GRS.Features.ExportStability.Backend.dll` | 导出稳定性检测特性 |

Shader Symbol 路径默认为：`{Project}/Saved/ShaderSymbols/`

## 模块依赖

### Public 依赖

| 模块 | 用途 |
|---|---|
| `InputDevice` | 输入设备抽象 |
| `RenderCore` | 渲染核心（RenderingThread 等） |

### Private 依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础库（路径、进程、日志） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入核心（按键绑定） |
| `Projects` | 插件管理 |
| `RHI` | 渲染硬件接口（NullRHI 检测） |

### Editor 专用依赖（仅 WITH_EDITOR）

| 模块 | 用途 |
|---|---|
| `Slate` / `SlateCore` | UI 框架 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器工具 |
| `MainFrame` | 主窗口管理 |
| `GameProjectGeneration` | 游戏项目生成 |
| `ToolMenus` | 工具栏菜单扩展 |
| `LevelEditor` | 关卡编辑器（动态加载） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-21 | `33b3a02` | GPU Reshape, moved out of restricted folder - Merged bin and symbol folders | 从受限文件夹迁移出来，合并了二进制和符号目录，这是插件集成的重要一步 |
| 2025-07-21 | `c5e645b` | GPU Reshape, added automatic symbol paths | 添加自动 Shader Symbol 路径配置，简化用户设置 |
| 2025-05-21 | `cade442` | Fixed bad option parsing for GPU Reshape branch | 修复命令行分支参数解析的 bug |

### 维护评价

- **创建时间**：2025-05-19，是非常新的插件（~1 年）
- **活跃度**：活跃维护中，2025 年 7 月仍有功能性更新
- **状态**：实验性质的新插件，VersionName 为 "0.1"
- **限制**：仅支持 Win64，需要第三方 GPU-Reshape 二进制文件存在于 `Engine/Binaries/ThirdParty/` 下
- **推荐**：如果你需要 GPU 层面的调试能力，值得一试；但由于版本 0.1 且仅限 Win64，生产环境使用需谨慎

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/GPUReshape)
- [GPU-Reshape 第三方源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/ThirdParty/GPUReshape)
- [GPU-Reshape GitHub（上游）](https://github.com/GPUOpen-Effects/GPU-Reshape)
- [GPU-Reshape 二进制](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Binaries/ThirdParty/GPUReshape)
