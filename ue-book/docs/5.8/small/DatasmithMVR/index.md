# Datasmith MVR

> Enabled support to import .udatasmith files with MVR content.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith MVR 导入器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithMVRTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-05-04 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DatasmithMVR) | |

## 用途

这个插件解决了 **Datasmith 场景导入时 MVR（My Virtual Rig）灯光数据丢失** 的问题。

MVR 是一种用于灯光行业交换 3D 灯具数据的标准格式（包含灯具位置、GDTF 灯具描述等信息）。当灯光设计师在 WYSIWYG、Capture 等预可视化软件中设计好灯光布局后，会生成 `.mvr` 文件。这些灯光数据通常需要与 Datasmith 场景一起导入到 UE 中。

此插件通过**重写 Datasmith 原生翻译器**（`FDatasmithNativeTranslator`），在导入 `.udatasmith` 文件时自动检测同目录或 `_Assets` 子目录中的 MVR 文件，将其解析为 `UDMXLibrary` 资产，并将场景中的 MVR 对应 Actor 替换为 MVR Scene Actor。这样，灯光设计师可以在 UE 中获得完整的虚拟灯光布置，无需手动重建。

## 使用场景

- 你从 WYSIWYG / Capture / Vectorworks 等灯光设计软件导出了 `.mvr` 文件，想在 UE 的虚拟制片环境中使用这些灯光数据 → 用此插件配合 Datasmith 一起导入
- 你需要将 Datasmith 建筑/场景数据与 DMX 灯具数据同步导入 → 将 `.mvr` 文件放在 `.udatasmith` 文件的 Assets 目录旁，导入 Datasmith 场景时自动处理
- 你的项目涉及虚拟制片灯光控制流程 → 需要此插件将预可视化灯光信息带入 UE

## 蓝图用法

此插件功能较底层，主要通过 Datasmith 导入流程自动触发，不暴露太多蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDatasmithMVRNativeTanslatorEnabled` | 启用或禁用 MVR 原生翻译器（模块启动时默认启用） | `IDatasmithMVRTranslatorModule` |

### 使用示例

1. **启用/禁用 MVR 翻译器**：
   - 获取 `DatasmithMVRTranslator` 模块接口
   - 调用 `SetDatasmithMVRNativeTanslatorEnabled(false)` 可禁用自动 MVR 处理

2. **导入包含 MVR 的 Datasmith 场景**：
   - 将 `.udatasmith` 文件和 `.mvr` 文件放在同一目录（或 `_Assets` 子目录中）
   - 通过 Datasmith 导入流程导入 `.udatasmith` 文件
   - 插件会自动检测并处理 MVR 文件

3. **导入选项配置**：
   - 在导入对话框中，可看到 `MVR` 分类下的 `Import MVR` 选项
   - 勾选此项（默认开启）表示将 MVR 对应的 Datasmith 元素替换为 GDTF Actor

## C++ 用法

### 头文件引入

```cpp
#include "IDatasmithMVRTranslatorModule.h"
```

### 基本用法

获取模块接口并控制翻译器的启用状态：

```cpp
// 检查模块是否已加载
if (FModuleManager::Get().IsModuleLoaded("DatasmithMVRTranslator"))
{
    IDatasmithMVRTranslatorModule& MVRModule = IDatasmithMVRTranslatorModule::Get();
    
    // 禁用 MVR 原生翻译器（默认已启用）
    MVRModule.SetDatasmithMVRNativeTanslatorEnabled(false);
    
    // 重新启用
    MVRModule.SetDatasmithMVRNativeTanslatorEnabled(true);
}
```

### 进阶用法

此插件的核心逻辑（`FDatasmithMVRNativeTranslator`）作为 Datasmith 原生翻译器的子类自动注册到 Datasmith 的翻译器管线中。工作流程：

1. **查找 MVR 文件**：`FindMVRFile()` 在 `.udatasmith` 文件旁或 `_Assets` 目录中查找 `.mvr` 文件
2. **创建 DMX Library**：`CreateDMXLibraryFromMVR()` 将 MVR 文件解析为 `UDMXLibrary` 资产
3. **替换 Actor**：`ReplaceMVRActorsWithMVRSceneActor()` 将场景中对应 MVR 条目的 Datasmith 元素替换为 MVR Scene Actor

这些方法均为内部实现，使用者无需直接调用。

## Demo 示例

此插件主要作为 Datasmith 导入管线的扩展，没有独立的可运行 Demo。以下为模块注册的最小示例：

```cpp
// MyModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
};

// MyModule.cpp
#include "MyModule.h"
#include "IDatasmithMVRTranslatorModule.h"

void FMyModule::StartupModule()
{
    // 确保 DatasmithMVRTranslator 模块已加载
    FModuleManager::Get().LoadModuleChecked<IDatasmithMVRTranslatorModule>("DatasmithMVRTranslator");
    
    // 此时 MVR 翻译器已自动注册到 Datasmith 管线
    // 任何后续的 .udatasmith 导入都会自动检测 MVR 文件
}

IMPLEMENT_MODULE(FMyModule, MyModule)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等及 Datasmith/DMX 相关模块）。

此插件隐式依赖以下 UE 模块（根据代码中的头文件引用推断）：

| 模块 | 用途 |
|---|---|
| `DatasmithContent` | Datasmith 场景数据结构和导入选项基类 |
| `DMXRuntime` | DMXLibrary 和 GDTF 灯具资产运行时支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符错误 |
| 2024-09-17 | `29962d04` | DMX: Remove experimental and beta flags from DMX plugins. All DMX plugins are now production ready | 移除实验性标志，DMX 插件正式转为生产就绪状态 |
| 2024-08-01 | `dca5f144` | Fixed some incorrect TSoftObjectPtr types. | 修复了部分 TSoftObjectPtr 类型错误 |
| 2023-07-24 | `ec0ca35c` | DMX - Fix MVR Import with Datasmith file adds DMX Library in content root | 修复了 MVR 导入时 DMX Library 错误放置在内容根目录的问题 |
| 2023-03-21 | `ddf065a8` | DMX - Fix an issue where datasmith importer doesn't save ports it updated, account for discrepancies | 修复了 Datasmith 导入器未保存已更新端口的问题 |

### 维护评价

- **创建时间**：2022 年 5 月，属于较新的 DMX 虚拟制片工具链的一部分
- **最近更新**：2026 年 2 月仍有编译修复，2024 年 9 月正式移除实验性标志，说明 Epic 已将其视为稳定功能
- **更新频率**：维护节奏较慢但持续，更新内容以 bug 修复为主
- **已知限制**：仅作为 Datasmith 导入流程的附加功能，不支持独立使用；源文件仅 6 个，功能较单一
- **推荐使用**：✅ 如果你的虚拟制片工作流涉及从预可视化软件导入 MVR 灯光数据，推荐启用此插件。它已在 2024 年正式标记为生产就绪。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DatasmithMVR)
- 测试用例：未发现独立测试文件