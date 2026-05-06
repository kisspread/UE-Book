# Cascade To Niagara Converter

> Add support for scriptable conversion of Cascade Systems to Niagara Systems.

| 属性 | 值 |
|---|---|
| 中文名 | Cascade 转 Niagara |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模板发射器资源） |
| 模块 | `CascadeToNiagaraConverter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/CascadeToNiagaraConverter) | |

## 用途

Cascade 粒子系统是 Unreal Engine 4 时代的旧式粒子特效系统，Niagara 是 UE5 新一代高性能、可扩展的粒子系统。此插件提供了一套**可脚本化的转换工具**，允许开发者将现有的 Cascade 粒子系统（`UParticleSystem`）一键/批量转换为 Niagara 系统（`UNiagaraSystem`），同时保留粒子参数、发射器设置、模块配置等核心逻辑。

插件通过扩展内容浏览器右键菜单，集成 Python 脚本支持，并暴露蓝图转换函数，解决了从旧系统迁移到新系统过程中的重复劳动和人为错误问题。

## 使用场景

- 你负责将已有 UE4 项目升级到 UE5，需要将数百个 Cascade 粒子系统转换为 Niagara。
- 你希望自动化转换流程，使用 Python 脚本批量处理，并在 CI 流程中校验转换结果。
- 你需要高度定制转换行为，例如自定义某些 Cascade 模块到 Niagara 模块的映射规则。

## 蓝图用法

插件提供了 `UNiagaraStackGraphUtilitiesAdapterLibrary` 蓝图函数库，用于在转换过程中操作 Niagara 栈图。核心节点包括：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert Cascade System to Niagara System` | 将指定的 Cascade 系统转换为 Niagara 系统，返回生成的 Niagara 资产路径 | `UNiagaraStackGraphUtilitiesAdapterLibrary` |
| `Create Niagara Emitter Conversion Context` | 创建发射器转换上下文，用于后续配置发射器参数 | `UNiagaraStackGraphUtilitiesAdapterLibrary` |
| `Add Emitter from Template` | 从模板添加发射器到转换上下文（支持 5.7 新功能） | `UNiagaraStackGraphUtilitiesAdapterLibrary` |

> 注：实际可调用的蓝图函数可能更多，建议在蓝图编辑器中搜索 "CascadeToNiagara" 查看完整列表。

### 使用示例（蓝图描述）

1. 获取目标 Cascade 粒子系统：通过 `Get Asset by Path` 获得 `ParticleSystem` 对象引用。
2. 调用 `Convert Cascade System to Niagara System`，输入该 `ParticleSystem` 引用和输出资产路径（例如 `/Game/Converted/`）。
3. 转换成功后，在指定路径生成对应的 `NiagaraSystem` 资产，可在内容浏览器中查看。

## C++ 用法

该插件主要通过编辑器菜单和蓝图/Python 脚本驱动，不暴露独立的 C++ API 供运行时调用。但你可以扩展其菜单行为或编写转换逻辑的模块。

### 头文件引入

```cpp
#include "CascadeToNiagaraConverterModule.h"
```

### 基本用法（通过编辑器菜单触发）

插件会在内容浏览器的选中资产右键菜单中添加"Convert to Niagara"选项。你无需编写任何 C++ 代码即可使用。

### 进阶用法（通过 Python 脚本）

由于插件依赖 `PythonScriptPlugin`，你可以使用 Python 进行批量转换：

```python
import unreal

# 获取转换器模块
converter = unreal.CascadeToNiagaraConverterModule.get()

# 选择所有 Cascade 资产
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
cascade_assets = asset_registry.get_assets_by_class("ParticleSystem")

# 执行转换
for asset in cascade_assets:
    converte.convert_cascade_system_to_niagara_system(asset.get_asset())
```

## Demo 示例

以下是一个最小 C++ 编辑器模块，演示如何以编程方式触发转换：

**MyConversionTool.h**

```cpp
#pragma once
#include "CascadeToNiagaraConverterModule.h"
#include "Modules/ModuleManager.h"

class FMyConversionTool
{
public:
    static void ConvertAllCascadeInFolder(const FString& FolderPath);
};
```

**MyConversionTool.cpp**

```cpp
#include "MyConversionTool.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "ICascadeToNiagaraConverterModule.h"

void FMyConversionTool::ConvertAllCascadeInFolder(const FString& FolderPath)
{
    // 获取资产注册表
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    TArray<FAssetData> AssetData;
    FARFilter Filter;
    Filter.ClassPaths.Add(FTopLevelAssetPath(TEXT("/Script/Engine"), TEXT("ParticleSystem")));
    Filter.PackagePaths.Add(*FolderPath);
    AssetRegistryModule.Get().GetAssets(Filter, AssetData);

    // 准备Cascade系统列表
    TArray<UParticleSystem*> CascadeSystems;
    for (const FAssetData& Data : AssetData)
    {
        if (UParticleSystem* Sys = Cast<UParticleSystem>(Data.GetAsset()))
        {
            CascadeSystems.Add(Sys);
        }
    }

    // 调用模块内置转换方法（通过静态方法，实际仅供内部菜单使用）
    // 注意：ExecuteConvertCascadeSystemToNiagaraSystem 是 private static，
    // 通常你应使用 Python 脚本或菜单操作。
    // 此处仅演示接口概念，实际请参考蓝图节点。
    // ICascadeToNiagaraConverterModule::ExecuteConvertCascadeSystemToNiagaraSystem(CascadeSystems);
}
```

> 提示：由于 `ExecuteConvertCascadeSystemToNiagaraSystem` 是私有静态方法，外部无法直接调用。更推荐的做法是使用 `PythonScriptPlugin` 驱动批量转换（见上方 Python 示例）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 提供目标 Niagara 系统、发射器、数据接口等核心类型 |
| `PythonScriptPlugin` | 支持 Python 脚本化执行转换 |
| `EditorScriptingUtilities` | 提供编辑器脚本操作（如资产创建、路径解析） |

> 无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

该插件在 UE 5.7 开发周期中创建并积极更新，属于活跃维护阶段。

### 近期更新

- 2025-09-03 `c339ca2b` — PR #13744: 允许从模板添加发射器。
- 2025-06-25 `049e4868` — 添加发射器/版本化发射器的基类。
- 2025-06-04 `0244d9f8` — PR #13323: 添加更多脚本输入类型。
- 2025-06-02 `883ac7b7` — PR #13322: 添加 `UPROPERTY()` 标签。
- 2025-05-31 `52e3dac1` — 使用 UnrealCodeFixup 更新头文件，确保 DLL 存储在方法和静态变量上。

### 维护评价

- **创建时间**：2025-05-31，至今约 0.4 年，非常年轻。
- **更新频率**：约每月 1~2 次功能性更新，且包含多个 Pull Request，说明社区有贡献。
- **活跃度**：最新更新在 2025-09-03，距离今天（2025-10-07）仅一个月，处于活跃维护中。
- **已知问题**：仍标记为 Beta 版本，可能存在接口不稳定或边缘情况未覆盖。
- **推荐使用**：适合需要进行 Cascade 迁移的团队，建议先在小范围测试确认转换效果。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/CascadeToNiagaraConverter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/cascade-to-niagara-converter-plugin/)（插件说明页，可能为空）