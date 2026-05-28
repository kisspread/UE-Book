# Cascade Editor

> Editor for (legacy) Cascade effect systems. Cascade assets can still run in a game with this plugin disabled.

| 属性 | 值 |
|---|---|
| 中文名 | 级联编辑器 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `Cascade` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-02-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Cascade) | |

## 用途

Cascade 是 Unreal Engine 中在 Niagara 之前的旧版粒子系统。本插件提供 Cascade 粒子系统的**编辑器工具**——即你双击 `.uasset` 粒子系统资产时打开的可视化编辑界面。

**关键点**：此插件仅包含编辑器功能。即使禁用本插件，Cascade 粒子系统资产仍然可以在游戏中正常运行和渲染。插件的目的是将 Cascade 编辑器从引擎代码中拆分为独立插件，便于维护和管理这个遗留系统。

编辑器提供的核心能力包括：
- 发射器（Emitter）和模块（Module）的可视化画布编辑
- 粒子系统的 3D 实时预览视口
- LOD 级别管理
- 曲线编辑器集成
- 模块的拖拽排序、复制、共享
- 缩略图生成

## 使用场景

- 你正在维护旧版 UE 项目，需要编辑 Cascade 粒子系统资产 → 使用本插件打开 `.uasset` 进行可视化编辑
- 你需要将旧版 Cascade 粒子系统迁移到 Niagara → 先用本插件查看和理解现有 Cascade 系统的结构
- 你的项目只需要运行 Cascade 粒子，不需要编辑 → 可以安全禁用此插件，减少编辑器内存占用

## 蓝图用法

本插件为纯编辑器模块，不提供任何 `BlueprintCallable` 节点。Cascade 粒子系统在运行时通过标准的 `UParticleSystemComponent` 驱动，与本插件无关。

## C++ 用法

本插件的核心 C++ API 是 `ICascadeModule` 接口，用于以编程方式创建和管理 Cascade 编辑器实例。

### 头文件引入

```cpp
#include "CascadeModule.h"
```

### 基本用法

通过 `ICascadeModule` 打开 Cascade 编辑器实例：

```cpp
// 获取 Cascade 模块
ICascadeModule& CascadeModule = FModuleManager::LoadModuleChecked<ICascadeModule>("Cascade");

// 创建一个新的 Cascade 编辑器实例
TSharedRef<ICascade> CascadeEditor = CascadeModule.CreateCascade(
    EToolkitMode::Standalone,  // 编辑器模式
    TSharedPtr<IToolkitHost>(), // Toolkit Host
    MyParticleSystem           // UParticleSystem* 要编辑的粒子系统
);
```

### 进阶用法

刷新已打开的编辑器实例或将模块转换为随机种子变体：

```cpp
ICascadeModule& CascadeModule = FModuleManager::LoadModuleChecked<ICascadeModule>("Cascade");

// 刷新正在编辑指定粒子系统的编辑器窗口
CascadeModule.RefreshCascade(MyParticleSystem);

// 将粒子系统中的所有模块转换为随机种子变体（用于提高性能）
CascadeModule.ConvertModulesToSeeded(MyParticleSystem);
```

## Demo 示例

以下示例展示如何在自定义编辑器工具中打开 Cascade 粒子系统进行编辑：

```cpp
// MyCascadeTool.h
#pragma once

#include "CascadeModule.h"

class FMyCascadeTool
{
public:
    /** 打开指定粒子系统的 Cascade 编辑器 */
    void OpenParticleSystemInCascade(UParticleSystem* ParticleSystem)
    {
        if (!ParticleSystem) return;

        ICascadeModule& CascadeModule = 
            FModuleManager::LoadModuleChecked<ICascadeModule>("Cascade");

        CascadeModule.CreateCascade(
            EToolkitMode::Standalone,
            nullptr,
            ParticleSystem
        );
    }

    /** 批量将粒子系统中的模块转换为种子模块 */
    void ConvertToSeededModules(UParticleSystem* ParticleSystem)
    {
        if (!ParticleSystem) return;

        ICascadeModule& CascadeModule = 
            FModuleManager::LoadModuleChecked<ICascadeModule>("Cascade");

        CascadeModule.ConvertModulesToSeeded(ParticleSystem);
    }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate/UnrealEd 等编辑器模块）。

本插件依赖以下引擎子系统（通过源码推断）：
- `Engine` — `UParticleSystem`、`UParticleEmitter`、`UParticleModule`、`UParticleSystemComponent` 等运行时粒子类型
- `UnrealEd` — `FAssetEditorToolkit`、`FEditorViewportClient`、`FPreviewScene` 等编辑器框架
- `Slate`/`SlateCore` — 编辑器 UI 控件（`SEditorViewport`、`SCompoundWidget`、`SScrollBar` 等）
- `InputCore` — 视口输入处理
- `RenderCore` — 曲线编辑器和渲染预览

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：将客户端关联/解除关联时的通知逻辑提取为公共方法 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了之前的某次提交 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：同上（被回退后再次提交） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-04-13 | `918bc423` | [Unreal Editor Localization] Fix localization issue | 修复编辑器本地化相关问题 |

### 维护评价

- **年龄**：插件本身创建于 2025 年 2 月（从引擎代码中拆分），但 Cascade 粒子系统本身是 UE 的古老功能（UE3 时代）
- **活跃度**：2026 年 4-5 月仍有持续更新，但均为**维护性改动**（代码重构、日志迁移、本地化修复），没有新功能
- **定位**：Legacy/遗留系统。编辑器中粒子系统资产已被标记为 `Deprecated` 分类，显示名为 "Cascade Particle System (Deprecated)"
- **推荐**：如果是新项目，**强烈建议使用 Niagara** 替代 Cascade。本插件仅适用于维护旧项目或理解旧版粒子系统资产

⚠️ **注意**：此插件的功能已标记为弃用（Deprecated）。即使启用，Cascade 粒子系统的编辑体验也不会再获得新功能改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Cascade)
- 官方文档：无
- 测试用例：位于引擎级自动化测试中（参见首次提交信息中提及的 "cascade automation tests"）