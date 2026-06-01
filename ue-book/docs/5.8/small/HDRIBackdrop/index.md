# HDRIBackdrop

> A plugin for placing HDRI environment map backdrops in the editor scene.

| 属性 | 值 |
|---|---|
| 中文名 | HDRI 背景板 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器放置工具） |
| 模块 | `HDRIBackdrop` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-08-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HDRIBackdrop) | |

## 用途

HDRIBackdrop 插件提供了一个编辑器内的快捷放置工具，让开发者能够快速在场景中添加一个带有 HDRI 环境贴图的背景球体。它解决了在关卡编辑器中快速搭建环境光照和背景的痛点——无需手动创建球体、分配材质再导入 HDRI 贴图，只需通过编辑器的放置面板（Placement Mode）一键放置即可。

该插件从 UE4.23 的内置功能中独立出来（Jira: UE-79150），作为一个可选的编辑器插件存在。

## 使用场景

- 你正在为产品可视化或建筑可视化项目搭建场景，需要快速添加 HDRI 环境背景 → 用 HDRIBackdrop
- 你在做场景光照参考，想快速预览 HDRI 贴图对场景的影响 → 用 HDRIBackdrop
- 你需要在编辑器中放置一个 360° 环境背景来辅助场景构图 → 用 HDRIBackdrop

> ⚠️ 该插件默认未启用，需在 **编辑 → 插件（Plugins）** 中手动搜索 "HDRI Backdrop" 并启用，重启编辑器后生效。

## 蓝图用法

该插件是一个纯编辑器放置工具，不暴露 BlueprintCallable 节点。使用方式完全通过编辑器 UI 操作完成：

### 使用步骤

1. 启用插件后，在编辑器左侧的 **放置面板（Place Actors）** 中找到新的 **HDRI Backdrop** 类别
2. 将 HDRI Backdrop Actor 拖拽到场景中
3. 在 Actor 的细节面板中指定 HDRI 环境贴图
4. 调整球体大小、旋转等参数

## C++ 用法

该插件主要提供编辑器扩展功能，不直接面向游戏运行时使用。以下是从源码中提取的模块接口用法。

### 头文件引入

```cpp
#include "HDRIBackdrop.h"
```

### 基本用法

插件以编辑器模块方式注册，启动时自动注册放置模式（Placement Mode）中的条目：

```cpp
// 模块启动入口 —— 自动注册放置面板入口
void FHDRIBackdropModule::StartupModule()
{
    // 注册放置模式中的 HDRI Backdrop 选项
    FHDRIBackdropPlacement::RegisterPlacement();
}

void FHDRIBackdropModule::ShutdownModule()
{
    // 清理样式资源
    FHDRIBackdropStyle::Shutdown();
}
```

### 进阶用法

如果需要在自定义编辑器扩展中复用 HDRI Backdrop 的样式：

```cpp
#include "HDRIBackdropStyle.h"

// 获取插件提供的 Slate 样式
TSharedPtr<ISlateStyle> Style = FHDRIBackdropStyle::Get();
```

## Demo 示例

该插件不需要编写代码即可使用，以下是典型工作流：

1. **启用插件**：编辑 → 插件 → 搜索 "HDRI Backdrop" → 启用 → 重启编辑器
2. **放置 Actor**：在放置面板中切换到 HDRI Backdrop 分类，拖入场景
3. **配置贴图**：选中 Actor，在细节面板中设置：
   - **HDRI 贴图**：指定一张 HDR 环境贴图
   - **球体大小**：控制背景球体的半径
   - **旋转角度**：调整环境贴图的朝向
   - **亮度**：调整环境光照强度

## 模块依赖

无特殊依赖（仅标准 Editor 框架和 Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录批量调整 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 预留头文件引入，为后续改动做准备 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的厂商链接为 HTTPS 安全协议 |
| 2021-01-26 | `d52549d8` | Placement Mode: shape category special icon handling and updates to plugins using FPlaceableItem | 放置模式分类图标处理更新，适配 FPlaceableItem 接口变更 |
| 2020-08-14 | `48113fc7` | Adding EditorFramework to build.cs files | 为 Build.cs 添加 EditorFramework 依赖 |

### 维护评价

HDRIBackdrop 是一个功能简单的编辑器小工具，自 2023 年 1 月起已无实质性功能更新（约 2.5 年）。最近的改动多为引擎级批量维护（协议更新、头文件清理等），而非插件本身的功能迭代。

- **维护状态**：不活跃，但代码稳定无需频繁修改
- **风险**：功能单一，依赖的编辑器 API 较稳定，不太会随引擎升级而失效
- **推荐**：如果你需要快速在场景中添加 HDRI 环境背景，推荐使用；如果需要更复杂的天空球或动态天空系统，应考虑引擎内置的 SkyAtmosphere 或自定义方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HDRIBackdrop)