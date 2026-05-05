# Mac Graphics Switching

> Provides support for switching between multiple graphics devices on macOS.

| 属性 | 值 |
|---|---|
| 分类 | Misc (Editor) |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | MacGraphicsSwitching (Editor) |
| 平台限制 | macOS only |
| 创建时间 | 2014-09-17 |
| 年龄标签 | 🏛️ 文物 (>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MacGraphicsSwitching) | |

## 用途

macOS 上某些 Mac（如 MacBook Pro）配备多个 GPU——集成显卡（如 Intel UHD）和独立显卡（如 AMD Radeon）。此插件允许用户在 UE5 编辑器中选择使用哪个 GPU 进行渲染。

插件的核心功能是：
1. **枚举系统中所有可用 GPU**，通过 `FPlatformMisc::GetGPUDescriptors()` 获取 GPU 列表
2. **提供下拉选择器**，让用户指定首选渲染设备
3. **设置 `Mac.ExplicitRendererID` 控制台变量**，通知引擎使用指定 GPU
4. **持久化选择**到 `EditorSettings.ini`，编辑器重启后保持选择

> **注意**：此插件仅在 macOS 上加载（`PlatformAllowList: ["Mac"]`），Windows/Linux 上不可用。

## 使用场景

- 你的 Mac 有多个 GPU（集成 + 独立），你想强制编辑器使用性能更强的独立显卡
- 你想测试游戏在不同 GPU（如集成显卡）上的表现
- 编辑器默认使用了错误的 GPU，需要手动切换

## 配置方法

### 通过编辑器设置面板

1. 打开 **Edit → Editor Preferences**（或 **Unreal Editor → Preferences**）
2. 导航到 **Plugins → Graphics Switching**
3. 在 **RHI** 分类下找到 **Preferred Renderer** 下拉菜单
4. 选择目标 GPU（显示为 `序号: GPU名称`，如 `1: AMD Radeon Pro 5500M`）
5. 选择 **System Default** 可恢复系统默认 GPU
6. **重启编辑器**使更改生效（设置标记为 `ConfigRestartRequired=true`）

### 配置项说明

| 配置项 | 类型 | 说明 |
|---|---|---|
| `RendererID` | int32 | 目标 GPU 的索引 ID。`-1` 表示使用系统默认 |
| `bShowGraphicsSwitching` | bool | 是否在编辑器工具栏显示 GPU 选择器（当前此功能已注释掉，见下文） |

配置存储路径：`/Script/MacGraphicsSwitching.MacGraphicsSwitchingSettings`

## 蓝图用法

此插件不提供任何 Blueprint API。它完全是编辑器 UI 功能，没有 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。

## C++ 用法

### 头文件引入

```cpp
#include "IMacGraphicsSwitchingModule.h"
```

### 检查模块可用性

```cpp
// 检查 MacGraphicsSwitching 模块是否已加载（仅在 macOS 上为 true）
if (IMacGraphicsSwitchingModule::IsAvailable())
{
    // 获取模块实例
    IMacGraphicsSwitchingModule& Module = IMacGraphicsSwitchingModule::Get();
}
```

### 枚举系统 GPU

```cpp
// 获取系统中所有 GPU 的描述信息（macOS only）
TArray<FMacPlatformMisc::FGPUDescriptor> const& GPUs = FPlatformMisc::GetGPUDescriptors();
for (FMacPlatformMisc::FGPUDescriptor const& GPU : GPUs)
{
    // GPU.GPUIndex   — GPU 索引号 (int32)
    // GPU.GPUName    — GPU 名称 (TCHAR[])
    // GPU.RegistryID — IOKit 注册表 ID (uint64)
}
```

### 读取当前选择的 GPU

```cpp
// 获取当前显式指定的渲染器索引
int32 ExplicitRendererId = FPlatformMisc::GetExplicitRendererIndex();
// 值为 0 表示系统默认，>0 表示指定的 GPU 索引
```

### 通过控制台变量切换 GPU

```cpp
// 查找并设置 Mac.ExplicitRendererID 控制台变量
static const auto CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("Mac.ExplicitRendererID"));
if (CVar)
{
    CVar->Set(1); // 设置为 GPU 索引 1
}
```

## 内部架构

插件由以下组件组成：

```
MacGraphicsSwitching/
├── MacGraphicsSwitching.uplugin
└── Source/MacGraphicsSwitching/
    ├── MacGraphicsSwitching.Build.cs
    ├── Public/
    │   └── IMacGraphicsSwitchingModule.h      ← 公共接口（Get/IsAvailable）
    └── Private/
        ├── MacGraphicsSwitchingModule.h/.cpp   ← 模块主类，注册设置面板
        ├── MacGraphicsSwitchingSettings.h/.cpp  ← UCLASS 配置对象
        ├── MacGraphicsSwitchingSettingsDetails.h/.cpp ← 设置面板自定义布局
        ├── MacGraphicsSwitchingWidget.h/.cpp    ← GPU 选择下拉框 Slate 控件
        └── MacGraphicsSwitchingStyle.h/.cpp     ← 自定义 Slate 样式
```

### 工作流程

1. **StartupModule** → 向 Settings 模块注册 `Editor > Plugins > MacGraphicsSwitching` 设置页
2. **注册 DetailCustomization** → 隐藏原始 `RendererID` 属性，替换为自定义 `SMacGraphicsSwitchingWidget` 下拉框
3. **SMacGraphicsSwitchingWidget** 构造时调用 `FPlatformMisc::GetGPUDescriptors()` 枚举 GPU
4. 用户选择 GPU → 写入 `GEditorSettingsIni` → 触发 `OnApplicationRestartRequired()`
5. 同时设置 `Mac.ExplicitRendererID` CVar（立即生效于当前会话）

### 关于工具栏 GPU 选择器

代码中存在将 GPU 选择器添加到编辑器工具栏的逻辑（`AddGraphicsSwitcher`），但**已被注释掉**。`bShowGraphicsSwitching` 配置项虽然存在，但目前不生效。用户只能通过 Editor Preferences 面板切换 GPU。

## Demo 示例

此插件不适用于项目集成。它是一个纯编辑器功能插件，由 Epic 内建提供，无需在项目中引用。

如需在自己的项目中实现 GPU 选择功能，可参考其核心逻辑：

```cpp
// 最简 GPU 切换逻辑（仅 macOS）
#if PLATFORM_MAC
#include "HAL/PlatformMisc.h"

void SwitchToGPU(int32 GPUIndex)
{
    // 通过 CVar 立即切换（当前会话生效）
    static const auto CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("Mac.ExplicitRendererID"));
    if (CVar)
    {
        CVar->Set(GPUIndex);
    }
    
    // 持久化到配置文件（重启后生效）
    GConfig->SetInt(
        TEXT("/Script/MacGraphicsSwitching.MacGraphicsSwitchingSettings"),
        TEXT("RendererID"),
        GPUIndex,
        GEditorSettingsIni
    );
    GConfig->Flush(false, GEditorSettingsIni);
}

TArray<FString> ListAvailableGPUs()
{
    TArray<FString> Result;
    Result.Add(TEXT("System Default"));
    
    TArray<FMacPlatformMisc::FGPUDescriptor> const& GPUs = FPlatformMisc::GetGPUDescriptors();
    for (auto const& GPU : GPUs)
    {
        Result.Add(FString::Printf(TEXT("%d: %s"), GPU.GPUIndex, *FString(GPU.GPUName)));
    }
    return Result;
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、平台抽象 |
| `CoreUObject` | UObject 系统（UCLASS 配置对象） |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统 |
| `LevelEditor` | 关卡编辑器扩展点 |
| `Slate` | UI 框架 |
| `PropertyEditor` | 设置面板自定义布局（私有） |
| `SlateCore` | Slate 核心渲染（私有） |
| `EditorFramework` | 编辑器框架（私有） |
| `UnrealEd` | 编辑器工具（私有） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2022-11-07 | `0a10c21` | Update Release-Engine-Staging from UE5/Main | 合并上游更新，无实质性功能变更 |
| 2022-11-03 | `404b10f` | Remove full path to public Core headers | 代码清理，修复头文件引用方式 |
| 2022-05-06 | `0743640` | Replacing legacy EditorStyle calls with AppStyle | 引擎 API 迁移（EditorStyle → AppStyle），非功能更新 |

### 维护评价

- **创建时间**：2014 年 9 月，已超过 11 年，属于 🏛️ 文物级插件
- **最后实质性更新**：无记录。所有近期 commit 都是编译修复和 API 迁移
- **活跃度**：**不活跃** — 超过 3 年没有功能更新
- **稳定性**：功能简单且稳定，不太需要频繁更新
- **特殊说明**：工具栏 GPU 选择器代码被注释掉，`bShowGraphicsSwitching` 配置项实际无效
- **推荐使用**：如果你在 Mac 上开发且有多个 GPU，这是唯一内建的 GPU 切换方案，仍然可用。但注意它只提供 Editor Preferences 面板入口，不提供工具栏快捷方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MacGraphicsSwitching)
- [官方文档]() — 无（DocsURL 为空）
