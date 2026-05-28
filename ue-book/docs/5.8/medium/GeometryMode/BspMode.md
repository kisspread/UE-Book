# Geometry Mode

> Geometry and BSP editing

| 属性 | 值 |
|---|---|
| 中文名 | 几何编辑模式 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器模式资产） |
| 模块 | `BspMode` (Editor), `GeometryMode` (Editor), `TextureAlignMode` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-28 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode) | |

## 用途

该插件将 BSP（Binary Space Partitioning）刷子编辑器、几何体编辑工具以及纹理对齐模式从引擎核心中提取出来，封装为可按需禁用的编辑器插件。BSP 刷子是 Unreal Engine 从初代就沿用至今的关卡搭建工具，允许关卡设计师使用基本几何体（立方体、球体、圆柱、楼梯等）快速构建场景原型。与使用静态网格体不同，BSP 刷子可在编辑器内实时 CSG 布尔运算（并集、差集、交集），非常适合白盒阶段。

插件拆分后，在特定平台或精简构建中可以完全禁用 BSP 功能，减小编辑器体积。

## 使用场景

- 你在做关卡白盒原型设计，需要快速搭建墙壁、地板、楼梯等基本形状
- 你需要使用 CSG 布尔运算在已有的 BSP 刷子上"挖洞"或合并形状
- 你需要精确对齐 BSP 表面的纹理（TextureAlignMode 提供的功能）
- 你希望在项目中完全禁用 BSP 功能以简化编辑器界面

## 蓝图用法

该插件主要面向编辑器扩展开发者，提供的公开 API 为 C++ 模块接口，**无 BlueprintCallable 节点**。所有交互通过编辑器 UI（放置模式面板中的 BSP 分类）完成。

### 核心节点

无蓝图可调用节点。BSP 刷子的使用通过编辑器的 **Place Actors** 面板完成：

1. 打开 **Place Actors** 面板（窗口 → 放置 Actor）
2. 切换到 **BSP** 分类
3. 拖拽所需的几何体到场景中
4. 在 **Details** 面板中调整刷子参数（大小、CSG 操作类型等）

## C++ 用法

### 头文件引入

```cpp
#include "IBspModeModule.h"
```

### 基本用法

注册自定义 BSP 构建器类型，使其出现在编辑器的 BSP 面板中：

```cpp
// 获取 BSP 模块实例
IBspModeModule& BspModeModule = FModuleManager::Get().LoadModuleChecked<IBspModeModule>("BspMode");

// 注册一个新的 BSP 构建器类型
BspModeModule.RegisterBspBuilderType(
    UMyCustomBrushBuilder::StaticClass(),   // 构建器类
    NSLOCTEXT("MyPlugin", "CustomBrush", "Custom Brush"),        // 显示名称
    NSLOCTEXT("MyPlugin", "CustomBrushTip", "A custom brush"),   // 提示文本
    FAppStyle::GetBrush("ClassIcon.BrushBuilder")                // 图标
);
```

### 进阶用法

在插件启动/关闭时管理 BSP 构建器类型的生命周期：

```cpp
void FMyPluginModule::StartupModule()
{
    IBspModeModule* BspModeModule = FModuleManager::Get().LoadModulePtr<IBspModeModule>("BspMode");
    if (BspModeModule)
    {
        BspModeModule->RegisterBspBuilderType(
            UMySphereBuilder::StaticClass(),
            FText::FromString(TEXT("My Sphere")),
            FText::FromString(TEXT("A custom sphere builder")),
            FAppStyle::GetBrush("ClassIcon.BrushBuilder")
        );
    }
}

void FMyPluginModule::ShutdownModule()
{
    IBspModeModule* BspModeModule = FModuleManager::Get().LoadModulePtr<IBspModeModule>("BspMode");
    if (BspModeModule)
    {
        // UE 5.8+ 使用 FName 变体
        BspModeModule->UnregisterBspBuilderType(UMySphereBuilder::StaticClass()->GetFName());
    }
}
```

> **注意**：`UnregisterBspBuilderType(UClass*)` 在 UE 5.8 中已废弃，应使用 `UnregisterBspBuilderType(FName)` 变体。

## Demo 示例

一个最小的自定义 BSP 构建器注册示例：

```cpp
// MyBspExtension.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyBspExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyBspExtension.cpp
#include "MyBspExtension.h"
#include "IBspModeModule.h"

void FMyBspExtensionModule::StartupModule()
{
    // BSP 模块可能未启用，需先检查
    if (FModuleManager::Get().IsModuleLoaded("BspMode"))
    {
        IBspModeModule& BspModeModule = FModuleManager::Get().LoadModuleChecked<IBspModeModule>("BspMode");

        BspModeModule.RegisterBspBuilderType(
            UMyBrushBuilder::StaticClass(),
            FText::FromString(TEXT("My Builder")),
            FText::FromString(TEXT("Creates my custom geometry")),
            nullptr  // 使用默认图标
        );
    }
}

void FMyBspExtensionModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("BspMode"))
    {
        IBspModeModule& BspModeModule = FModuleManager::Get().LoadModuleChecked<IBspModeModule>("BspMode");
        BspModeModule.UnregisterBspBuilderType(UMyBrushBuilder::StaticClass()->GetFName());
    }
}

IMPLEMENT_MODULE(FMyBspExtensionModule, MyBspExtension)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件是编辑器模式插件，依赖常见的编辑器基础设施模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退了某次变更 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 工具栏添加全局吸附开关及红色状态指示器 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 UE_LOGF |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的 PVS 静态分析抑制项 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the <Source>To<Target> pattern for transforms, to reduce ambi | 重命名视图矩阵成员以遵循 Source→Target 命名规范 |

### 维护评价

该插件创建于 2019 年，是将引擎内置 BSP 编辑功能拆分为独立插件的结果。从 git 历史看，最近一年（2026 年初至今）仍有功能性更新（全局吸附开关）和持续的代码维护工作（日志迁移、静态分析清理），表明仍在**活跃维护**。

作为 Epic 官方维护的核心编辑器功能，BSP 编辑工具在可预见的未来仍将保留在引擎中。不过需注意 BSP 刷子本身是较老的技术方案，现代关卡设计流程更推荐使用静态网格体。对于新项目，建议仅在白盒阶段使用 BSP，最终替换为正式资产。

**推荐使用**：✅ 对于需要 BSP 编辑功能的项目，该插件默认启用，无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode)
- 官方文档：无
- 测试用例：未在该插件目录内发现独立测试文件