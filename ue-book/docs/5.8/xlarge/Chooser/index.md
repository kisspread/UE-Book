# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 中文名 | 动态选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产模板） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Editor), `ChooserUncooked` (UncookedOnly), `ProxyTable` (Runtime), `ProxyTableEditor` (Editor), `ProxyTableUncooked` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一套**数据驱动的动态资产选择系统**，核心解决的问题是：在运行时根据上下文条件（如角色状态、属性值、GameplayTag 等）从一组候选资产中自动选出最匹配的结果。

它由两个互补部分组成：

- **Chooser Table（选择表）**：类似 Excel 表格的条件查询结构。每行代表一个候选资产，每列代表一个条件/输入属性。运行时根据当前上下文值匹配行列，返回最佳资产。适用于动画选择、武器切换、技能映射等场景。
- **Proxy Table（代理表）**：为任意 UObject 类型提供间接引用层，支持运行时动态替换实际指向的资产。常用于实现不同角色对同一槽位引用不同资源（如不同角色播放不同动画）。

两个系统通常配合使用：Chooser Table 负责"选什么"，Proxy Table 负责"怎么引用"。插件从 Experimental 毕业后已作为正式功能发布。

## 使用场景

- 你有一组角色动画，需要根据移动速度、方向、装备状态等条件自动选择播放哪个 → 用 Chooser Table
- 你需要让不同角色类型（如战士/法师）对同一个动画槽位使用不同动画资产 → 用 Proxy Table
- 你在做装备系统，不同武器类型需要映射到不同的动画蒙太奇 → 用 Chooser Table + Proxy Table 组合
- 你需要美术或策划通过可视化表格配置资产映射逻辑，而非写代码 → 用 Chooser 的编辑器 UI

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `Chooser` | Runtime | 核心运行时逻辑：Chooser Table 的评估引擎、Proxy Table 的资产解析 |
| `ChooserEditor` | Editor | Chooser Table 的编辑器 UI：表格编辑器、列配置、资产预览 |
| `ChooserUncooked` | UncookedOnly | Chooser 的序列化/反序列化支持，确保打包前数据正确处理 |
| `ProxyTable` | Runtime | Proxy Table 运行时逻辑：间接资产引用、运行时动态替换 |
| `ProxyTableEditor` | Editor | Proxy Table 的编辑器 UI：代理条目编辑、资产浏览 |
| `ProxyTableUncooked` | UncookedOnly | Proxy Table 的序列化/反序列化支持 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateChooser` | 根据上下文评估 Chooser Table，返回选中的资产 | `UChooserTable` |
| `GetProxyResult` | 从 Proxy Table 获取当前代理指向的实际资产 | `UProxyTable` |

> ⚠️ 需要手动启用插件后才能在蓝图中使用相关节点。

## C++ 用法

### 头文件引入

```cpp
#include "ChooserFunctionLibrary.h"
#include "ChooserTable.h"
#include "ProxyTable.h"
```

### 基本用法

```cpp
// 通过 Chooser Table 根据上下文选择动画资产
UChooserTable* ChooserTable = LoadObject<UChooserTable>(nullptr, TEXT("/Game/Data/AnimChooser"));
UObject* Result = UChooserFunctionLibrary::EvaluateChooser(this, ChooserTable, UAnimMontage::StaticClass());
if (UAnimMontage* Montage = Cast<UAnimMontage>(Result))
{
    PlayAnimMontage(Montage);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 条件列支持基于 GameplayTag 的匹配查询 |
| `StructUtils` | 结构体属性访问（Chooser 表列值的统一处理） |

依赖关系已在插件声明中注册 `GameplayTagsEditor` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `aad6fe75` | Remove build setting making chooser internal headers public, and move most of those internal headers | 清理内部头文件的公开访问权限，收紧 API 边界 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `333cccbc` | Add profiling tag to chooser property access | 为 Chooser 属性访问添加性能分析标签 |
| 2026-04-17 | `1eda8a87` | Fix chooser editor null pointer crash after native context type rename | 修复原生上下文类型重命名后编辑器空指针崩溃 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器新增数据资产创建菜单支持 |

### 维护评价

插件于 2024 年 9 月从 Experimental 毕业正式发布，至今约 1 年。最近的更新（2026 年 5 月）集中在 **API 清理、性能分析、Bug 修复**，表明 Epic 内部有持续使用和打磨此系统。

- ✅ **活跃维护**：近一个月内有 5 次提交，包含功能增强和稳定性修复
- ✅ **非实验性**：已从 Experimental 正式毕业
- ⚠️ **默认未启用**：`EnabledByDefault=false`，需在项目设置中手动启用
- ⚠️ **API 仍在演进**：近期有头文件可见性调整，说明公开 API 尚未完全稳定

**推荐使用**：如果你的项目需要数据驱动的动画/资产选择逻辑，Chooser 是官方推荐的方案。但注意 API 可能随版本更新变化，升级时需关注 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)
- [Chooser 模块文档](Chooser.md)
- [ChooserEditor 模块文档](ChooserEditor.md)
- [ChooserUncooked 模块文档](ChooserUncooked.md)
- [ProxyTable 模块文档](ProxyTable.md)
- [ProxyTableEditor 模块文档](ProxyTableEditor.md)
- [ProxyTableUncooked 模块文档](ProxyTableUncooked.md)