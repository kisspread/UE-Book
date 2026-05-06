# Cascade Editor

> Editor for (legacy) Cascade effect systems. Cascade assets can still run in a game with this plugin disabled.

| 属性 | 值 |
|---|---|
| 中文名 | Cascade 编辑器 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器界面资源配置） |
| 模块 | `Cascade` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-02-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Cascade) | |

---

## 用途

Cascade 编辑器是 UE5 中用于编辑**旧版（Legacy）粒子系统**的工具。  
它提供完整的粒子发射器、模块、LOD 和预览界面，允许你调整和预览 `UParticleSystem` 资产的效果。

**为什么存在？**  
在 UE4 时代，Cascade 是标准的粒子编辑器。UE5 引入 Niagara 作为新一代粒子系统后，Cascade 被标记为 **Deprecated（已弃用）**，但引擎仍然保留该插件，以便：

- 打开和编辑已有项目中的 Cascade 粒子资产。
- 在关闭插件时，已完成的 Cascade 粒子仍能在运行时正常播放。
- 为迁移到 Niagara 提供过渡支持。

---

## 使用场景

- **维护旧项目**：如果你正在接手或维护一个使用 Cascade 粒子系统的 UE4/5 旧项目，需要此插件来观察和修改粒子效果。
- **资源迁移**：将旧版 Cascade 粒子手动转换为 Niagara 系统时，需要 Cascade 编辑器作为参考源。
- **兼容性测试**：验证旧粒子在 UE5 下是否仍然按预期运行（无需编辑，只需启用插件）。

---

## 蓝图用法

本插件为编辑器专用，**不提供任何公开的蓝图可调用函数或可读写属性**。  
所有操作均在编辑器的 Cascade 标签页内完成。

---

## C++ 用法

### 头文件引入

```cpp
#include "CascadeModule.h"
```

### 基本用法

通过模块接口 `ICascadeModule` 可编程打开 Cascade 编辑器：

```cpp
UParticleSystem* MyParticleSystem = LoadObject<UParticleSystem>(nullptr, TEXT("/Game/MyParticles.MyParticles"));
if (MyParticleSystem)
{
    ICascadeModule* CascadeModule = FModuleManager::LoadModulePtr<ICascadeModule>("Cascade");
    if (CascadeModule)
    {
        TSharedRef<ICascade> CascadeEditor = CascadeModule->CreateCascade(
            EToolkitMode::Standalone,
            TSharedPtr<IToolkitHost>(),
            MyParticleSystem
        );
    }
}
```

*来源：* `Source/Cascade/Public/CascadeModule.h`（接口定义）

### 进阶用法

- **监听编辑器关闭**：实现 `CascadeClosed` 回调（在 `ICascadeModule` 中定义）。
- **刷新编辑器**：当外部修改粒子系统资产后，调用 `RefreshCascade(MyParticleSystem)`。
- **批量转换模块**：使用 `ConvertModulesToSeeded` 将所有模块转换为种子模块（保留现有配置）。

```cpp
// 刷新所有打开该粒子系统的 Cascade 编辑器
ICascadeModule* CascadeModule = FModuleManager::GetModulePtr<ICascadeModule>("Cascade");
if (CascadeModule)
{
    CascadeModule->RefreshCascade(MyParticleSystem);
}
```

---

## Demo 示例

无公开可编译的最小示例。Cascade 编辑器的使用完全集成在编辑器中：  
右键任意 **Particle System** 资产 → **Open in Cascade Editor**。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Engine / UnrealEd / Slate 等模块 |

（该插件为纯编辑器工具，不引入独特的外部依赖）

---

## 维护状态

### 近期更新

- 2025-06-24 `2d5b420a` — Deprecated BuildFeatureLevelWidget, LoadEditorFeatureLevel, SaveEditorFeatureLevel for BuildShaderPlat
- 2025-06-10 `bb3758b4` — SEditorViewport::MakeViewportToolbar() is deprecated.
- 2025-02-24 `38a2c310` — [Input]
- 2025-02-21 `f9c3969a` — Move Cascade editor into its own plugin

### 维护评价

- **创建时间**：2025-02-21（约 3 个月前）
- **最近更新频率**：活跃（2025-06-24 有更新）
- **活跃度**：仍在维护（主要随引擎代码重构而同步更新）
- **已知问题**：Cascade 已被官方标记为 **Deprecated（弃用）**，未来可能移除或不再增加新功能。
- **推荐使用**：仅用于维护旧项目中的 Cascade 粒子系统；**新项目请使用 Niagara**。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Cascade)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/cascade-particle-system-in-unreal-engine/)（Cascade 概述页）
- [迁移到 Niagara 指南](https://docs.unrealengine.com/5.7/en-US/particle-system-migration-from-cascade-to-niagara-in-unreal-engine/)