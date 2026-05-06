# USD Importer MDL integration

> Allows importing USD files that reference MDL files, via the USD Stage Actor and USD import

| 属性 | 值 |
|---|---|
| 中文名 | USD MDL 材质集成 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDImporterMDL` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporterMDL) | |

## 用途

USD 场景中经常引用 [MDL（Material Definition Language）](https://www.nvidia.com/en-us/design-visualization/technologies/material-definition-language/) 材质，例如从 NVIDIA Omniverse 导出的 USD 文件可能包含 MDL 着色器。  
该插件扩展了 UE 的 USD 导入管线，使得在导入 USD 文件或使用 USD Stage Actor 加载场景时，能够自动识别并翻译 MDL 材质定义，将其转换为 UE 的材质系统。它依赖 `MDLImporter` 插件实现 MDL 解析，并集成到标准 `USDImporter` 工作流中。

## 使用场景

- 你从外部工具（如 Omniverse、DCC 应用）导入了包含 MDL 材质引用的 USD 文件 → 本插件会负责将 MDL 材质翻译为 UE 材质实例
- 你希望在使用 USD Stage Actor 动态加载场景时也能自动处理 MDL 材质 → 无需额外手动操作
- 你的项目需要与使用 MDL 标准的第三方资产库进行交互

## 蓝图用法

本插件为编辑器模块，不暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。  
所有功能集成在 USD 导入 / 加载流程中，蓝图侧无需额外节点。  
如果你需要手动控制材质翻译行为，请使用 USDImporter 插件提供的标准蓝图接口（如 `Import USD File`、`Get USD Stage Actor` 等）。

## C++ 用法

### 头文件引入

```cpp
#include "MDLUSDShadeMaterialTranslator.h"
```

### 基本用法

插件自动注册翻译器 `FMdlUsdShadeMaterialTranslator`，当 USD 中的材质使用 MDL 渲染上下文（`UnrealIdentifiers::MdlRenderContext`）时，该翻译器会接管材质创建。  
你不需要手动实例化该类，只需确保插件已启用且 `MDLImporter` 插件可用。

### 进阶用法

如果需要自定义 MDL 材质翻译逻辑，可以继承 `FMdlUsdShadeMaterialTranslator` 并重写 `CreateAssets` 方法。  
示例（来自插件源码）：

```cpp
// MdlUSDShadeMaterialTranslator.h
class FMdlUsdShadeMaterialTranslator : public FMaterialXUsdShadeMaterialTranslator
{
public:
    using FMaterialXUsdShadeMaterialTranslator::FMaterialXUsdShadeMaterialTranslator;

    virtual void CreateAssets() override;
};
```

在 `CreateAssets` 中执行 MDL 材质到 UE 材质的转换。基类 `FMaterialXUsdShadeMaterialTranslator` 提供了材质翻译的基础框架。

## Demo 示例

本插件无需额外代码示例；启用后，导入含 MDL 材质的 USD 文件即可自动触发。  
下面给出一个最小验证步骤：

1. 确保已启用插件 `USDImporterMDL`、`USDCore`、`USDImporter`、`MDLImporter`
2. 准备一个包含 MDL 材质的 USD 文件（例如 `material.mdl` 引用）
3. 在编辑器中点击 **File → Import Into Level**，选择该 USD 文件
4. 观察导入结果：MDL 材质被转换为 UE 材质实例，并正确赋予网格体

## 模块依赖

当你自己的模块需要使用本插件（例如继承翻译器）时，需在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `USDImporterMDL` | 当前插件主模块（Editor 类型） |
| `USDCore` | USD SDK 基础核心 |
| `USDImporter` | USD 导入框架 |
| `MDLImporter` | MDL 材质解析与转换 |

注意：本插件仅在 Editor 环境下编译，不会打包到最终游戏中。

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 USD: Disabled UE allocator in USD for Windows.  
- 2025-10-17 be609b71 [Backout] - CL47041219  
- 2025-10-17 7ab79237 USD: Disabled UE allocator in USD for Windows.  
- 2025-09-15 d7ab5176 For merged module only enable python if it's set to be compiled by the target and in editor.  
- 2025-09-09 4f303d57 Disabled UE allocators in OpenUSD for Linux.

### 维护评价

插件创建于 2025 年 9 月，属于全新实验性功能。近期提交多为 USD 全局基础设施调整（如内存分配器），未发现针对本插件自身功能的独立修复或增强。目前处于活跃维护中（至少与 USD 管线同步更新）。由于是 Beta 版本，建议在正式项目中试用前充分验证兼容性。已知限制：依赖 `MDLImporter` 插件，且 MDL 翻译仅在 Editor 环境下生效。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporterMDL)
- [官方文档](https://docs.unrealengine.com/5.7/WorkingWithUSD)（USD 工作流总览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporterMDL/Source)（暂无专用测试）