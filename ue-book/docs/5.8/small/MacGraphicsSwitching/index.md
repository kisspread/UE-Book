# Mac Graphics Switching

> Provides support for switching between multiple graphics devices on macOS.

| 属性 | 值 |
|---|---|
| 中文名 | Mac图形切换 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MacGraphicsSwitching` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-17 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MacGraphicsSwitching) | |

## 用途

该插件专为 macOS 平台设计，用于解决在拥有多个图形处理器（GPU）的 Mac 电脑（如 MacBook Pro）上，无法在 Unreal Editor 内灵活选择和管理活动图形设备的问题。macOS 系统默认可能会自动切换 GPU，而此插件允许开发者在编辑器中**主动、明确地选择**要使用哪个 GPU（例如，强制使用性能更强的独立显卡，或出于省电考虑使用集成显卡），并支持**实时切换**，无需重启编辑器，从而优化开发时的图形性能与功耗平衡。

## 使用场景

- 你正在使用一台拥有独立显卡和集成显卡的 Mac 电脑（如 MacBook Pro）进行 UE5 项目开发。
- 你希望编辑器在渲染视口或处理复杂场景时使用高性能的独立显卡，以获得更流畅的体验。
- 或者，你希望在长时间编码或简单编辑时切换到集成显卡以延长笔记本电脑的电池续航。
- 你需要一个直观的编辑器界面来查看当前可用的图形设备并进行快速切换，而不是修改晦涩的配置文件。

## 蓝图用法

该插件主要通过编辑器 UI 提供功能，但其设置项暴露给蓝图（通过 UObject 配置）。

### 核心设置类

| 属性 | 说明 | 所在类 |
|---|---|---|
| `RendererID` | 指定要使用的渲染器（GPU）ID。修改后需要重启编辑器生效。 | `UMacGraphicsSwitchingSettings` |
| `bShowGraphicsSwitching` | 是否在编辑器主窗口（关卡编辑器）显示 GPU 实时选择下拉菜单。 | `UMacGraphicsSwitchingSettings` |

### 使用示例（蓝图描述）

此功能主要通过编辑器 UI 使用：
1.  通过 **编辑器 -> 编辑器偏好设置 -> RHI** 路径找到“Mac Graphics Switching”设置面板。
2.  在“Preferred Renderer”下拉框中，选择你希望默认使用的 GPU。
3.  勾选“Show Editor GPU Selector”，然后在主编辑器窗口的工具栏区域将出现一个实时 GPU 选择器下拉菜单，允许你在编辑器运行时动态切换活动 GPU。

## C++ 用法

插件提供了模块接口用于程序化检查，但通常不需要直接操作。

### 头文件引入

```cpp
#include "IMacGraphicsSwitchingModule.h"
```

### 基本用法

检查 MacGraphicsSwitching 模块是否可用并获取其接口。这通常用于条件性地集成依赖于该功能的其他逻辑。

```cpp
// 检查模块是否已加载并可用
if (IMacGraphicsSwitchingModule::IsAvailable())
{
    // 获取模块单例引用
    IMacGraphicsSwitchingModule& MacGraphicsModule = IMacGraphicsSwitchingModule::Get();
    // 可以在此处调用模块提供的特定功能（如果存在）
}
```

### 进阶用法

目前该模块接口未暴露额外的公共函数，主要功能由编辑器 UI 和配置系统驱动。

## Demo 示例

以下是一个最小的 C++ 示例，演示如何在你的插件或模块中查询 `MacGraphicsSwitching` 模块的状态。

**MyModule.cpp**
```cpp
#include "MyModule.h"
#include "IMacGraphicsSwitchingModule.h"

void FMyModule::StartupModule()
{
    // 在模块启动时，检查 Mac 图形切换功能是否可用
    if (IMacGraphicsSwitchingModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("MacGraphicsSwitching module is available. GPU switching features may be accessible."));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("MacGraphicsSwitching module is not available."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复不支持可移植工具链的模块 |
| 2026-01-24 | `da0ea9af` | Fixed compile errors when compiling UnrealEditor with portable toolchain | 修复使用可移植工具链编译编辑器时的编译错误 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复使用可移植工具链时的更多编译错误 |
| 2022-11-04 | `3ed2a97d` | Remove full path to public Core headers | 移除公共Core头的完整路径 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接以使用安全协议 |

### 维护评价

- **状态**: **维护不活跃**。自 2014 年创建以来，该插件长期处于稳定状态。最近的提交（2026年）均是针对新工具链的编译兼容性修复，而非功能更新或错误修复。上一次实质性代码改动或功能更新可追溯至 2022 年之前。
- **平台限制**: 仅限 macOS 平台，且 `PlatformAllowList` 明确指定了 `Mac`。
- **推荐度**: **仅限 Mac 用户推荐使用**。如果你在 Mac 上进行 UE5 开发，并且需要手动管理 GPU 选择以优化性能或功耗，那么这个插件是必需的且默认启用的。对于 Windows/Linux 用户或不需要此功能的 Mac 用户，可以安全地忽略。鉴于其年龄和低频更新，使用时应关注未来版本兼容性，但当前功能稳定可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MacGraphicsSwitching)
- 官方文档链接不可用
- 测试用例未在插件目录内发现