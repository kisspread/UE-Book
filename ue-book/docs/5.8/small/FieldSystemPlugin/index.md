# Field System Plugin

> Analytic Field

| 属性 | 值 |
|---|---|
| 中文名 | 场系统编辑器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（图标资源） |
| 模块 | `FieldSystemEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-12-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FieldSystemPlugin) | |

## 用途

这是 **Field System（场系统）** 的**编辑器支持插件**，为引擎内置的 `UFieldSystem` 资产提供创建、编辑和管理的编辑器集成能力。

Field System 是一种用于定义空间中解析场（Analytic Field）数据的资产，通常配合 **Chaos Destruction（Chaos 破坏系统）** 使用，用于控制破坏效果中的力场分布。例如：
- 在几何体破坏时施加径向力
- 定义重力方向和强度的空间变化
- 创建自定义力场来影响物理模拟

> ⚠️ **注意**：此插件仅提供编辑器侧的资产管理和 UI 支持。`UFieldSystem` 类本身、场节点（Field Nodes）等运行时逻辑位于引擎核心模块中，不在此插件范围内。

## 使用场景

- 你正在使用 **Chaos Destruction** 系统并需要创建自定义力场资产 → 启用此插件
- 你需要为破碎效果定义空间中的力分布（径向力、线性力、随机力等） → 创建 Field System 资产
- 你在编辑器中需要一个可视化的场资产管理入口 → 此插件提供资产类型图标和缩略图

## 蓝图用法

此插件本身不暴露蓝图节点，它是一个纯编辑器集成插件，提供：

| 功能 | 说明 |
|---|---|
| 资产创建 | 通过 Content Browser 创建 `UFieldSystem` 资产 |
| 资产编辑 | 双击资产打开专用编辑器 |
| 资产分类 | 在 Content Browser 的 **Physics** 分类下显示 |
| 拖放支持 | 将资产拖入关卡自动创建 `AFieldSystem` Actor |

## C++ 用法

此插件主要面向引擎内部使用，不提供公开的 C++ API 供游戏模块调用。以下为内部用法说明：

### 头文件引入

```cpp
#include "FieldSystemEditorModule.h"
```

### 基本用法

```cpp
// 检查 FieldSystem 编辑器模块是否可用
if (IFieldSystemEditorModule::IsAvailable())
{
    IFieldSystemEditorModule& EditorModule = IFieldSystemEditorModule::Get();
}
```

> 来源：`Source/FieldSyStemEditor/Public/Field/FieldSystemEditorModule.h`

### 进阶用法 — 自定义资产工厂

```cpp
// 创建 FieldSystem 资产（静态工厂方法）
UFieldSystem* FieldSystem = UFieldSystemFactory::StaticFactoryCreateNew(
    UFieldSystem::StaticClass(),
    InParent,
    FName("MyFieldSystem"),
    RF_Transactional,
    nullptr,
    GWarn
);
```

> 来源：`Source/FieldSyStemEditor/Public/Field/FieldSystemFactory.h`

## Demo 示例

此插件为编辑器集成插件，无需编写代码。使用方式：

1. 在插件设置中启用 **Field System** 插件
2. 重启编辑器
3. 在 Content Browser 中右键 → **Physics** → **Field System**
4. 双击创建的资产进入编辑器
5. 在场编辑器中添加场节点（Field Nodes）定义力场分布

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

> 由于插件源码中未提供 Build.cs 详细内容，从代码分析仅使用了标准引擎模块（UFactory、FAssetTypeActions、UActorFactory 等均为引擎基础类）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复重复符号链接错误 |
| 2023-11-15 | `b64f2e25` | [Deprecation Cleanup] Remove deprecated code in actor factory class | 清理 ActorFactory 中已废弃的代码 |
| 2023-02-17 | `73c74eaf` | Removing redundant include paths: | 移除冗余的头文件包含路径 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量重构/路径调整 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议 |

### 维护评价

- **年龄**：约 7 年，属于实验性遗留插件
- **更新频率**：最近几年的更新均为编译修复和代码清理，无功能性更新
- **活跃度**：**不活跃**。插件功能极其精简（仅编辑器集成），已趋于稳定
- **已知限制**：
  - 标记为 `IsBetaVersion = true`，从未达到正式版
  - `EnabledByDefault = false`，需手动启用
  - 核心功能（FieldSystem 运行时）已集成到引擎主体中，此插件仅为编辑器壳
- **推荐程度**：如果你使用 Chaos Destruction 系统，此插件是**必需的**（否则无法在编辑器中创建 FieldSystem 资产）。但无需关注其源码，它是纯基础设施。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FieldSystemPlugin)
- 官方文档：无
- 测试用例：无