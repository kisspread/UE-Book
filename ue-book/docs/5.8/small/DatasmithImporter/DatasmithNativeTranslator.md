# Datasmith Native Translator

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith原生翻译器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithNativeTranslator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithNativeTranslator 是 Datasmith 导入管线中的**核心翻译器模块**，负责将 `.udatasmith` 原生格式文件解析为 UE 可识别的资产数据。

**解决的问题**：Datasmith 支持从多种 CAD/BIM/3D 软件（如 Revit、SketchUp、3ds Max 等）导出的文件导入到 Unreal Engine。不同来源的文件格式各异，Datasmith 采用"翻译器（Translator）"架构——每种格式由独立的 Translator 实现负责解析。本模块是其中的**原生翻译器**，专门处理 Datasmith 自有的 `.udatasmith` 文件格式。

**架构位置**：
```
DatasmithImporter (主插件)
├── DatasmithTranslator (翻译器接口层 - IDatasmithTranslator)
├── DatasmithNativeTranslator ← 本模块（原生格式翻译器）
├── DatasmithExternalSource
└── DirectLinkExtension (实时链接)
```

本模块实现了 `IDatasmithTranslator` 接口，提供场景加载（`LoadScene`）、静态网格加载（`LoadStaticMesh`）、关卡序列加载（`LoadLevelSequence`）等核心功能。

## 使用场景

- 你从 Revit、3ds Max、SketchUp 等软件通过 Datasmith Exporter 插件导出了 `.udatasmith` 文件，需要导入到 UE 场景中 → 本模块自动参与导入流程
- 你在做建筑可视化（ArchViz）项目，需要将 BIM 模型精确导入并保留层级、材质和元数据 → 使用 Datasmith 管线
- 你需要通过 DirectLink 实现设计软件与 UE 之间的实时同步 → DirectLink 底层也依赖本翻译器进行数据转换
- 你需要导入关卡序列动画（LevelSequence）→ `LoadLevelSequence` 支持

## 蓝图用法

本模块主要在引擎内部的 Datasmith 导入管线中工作，不直接暴露蓝图节点。Datasmith 导入操作通过以下方式触发：

- **编辑器菜单**：File → Import Into Level → 选择 `.udatasmith` 文件
- **Datasmith Scene Actor**：在场景中放置 Datasmith Scene Actor，指定 `.udatasmith` 文件
- **DirectLink**：通过 DirectLink 实时接收来自 CAD 软件的场景数据

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithNativeTranslator.h"
```

### 基本用法

DatasmithNativeTranslator 是 `IDatasmithTranslator` 接口的实现类。一般不需要直接实例化，Datasmith 导入框架会自动发现并使用注册的翻译器。但如果你需要自定义导入流程或扩展翻译器功能，可以参考其接口：

```cpp
#include "DatasmithNativeTranslator.h"
#include "DatasmithTranslator.h"

// 创建一个原生翻译器实例
TSharedPtr<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();

// 获取翻译器能力描述
FDatasmithTranslatorCapabilities Capabilities;
Translator->Initialize(Capabilities);

// Capabilities 包含该翻译器支持的特性：
// - 是否支持场景加载
// - 是否支持网格加载
// - 是否支持关卡序列等
```

### 进阶用法

**加载完整场景**：

```cpp
#include "DatasmithNativeTranslator.h"
#include "DatasmithSceneFactory.h"

// 创建翻译器和目标场景
TSharedPtr<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();

// 初始化翻译器
FDatasmithTranslatorCapabilities Capabilities;
Translator->Initialize(Capabilities);

// 加载场景到 IDatasmithScene 对象
TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyScene"));
bool bSuccess = Translator->LoadScene(Scene);

if (bSuccess)
{
    // 场景加载成功，遍历元素
    for (int32 i = 0; i < Scene->GetMeshesCount(); ++i)
    {
        TSharedPtr<IDatasmithMeshElement> MeshElement = Scene->GetMesh(i);
        if (MeshElement.IsValid())
        {
            // 使用翻译器加载网格体数据
            FDatasmithMeshElementPayload MeshPayload;
            Translator->LoadStaticMesh(MeshElement.ToSharedRef(), MeshPayload);
            
            // MeshPayload 包含网格几何数据、材质槽等信息
        }
    }
    
    // 加载关卡序列
    for (int32 i = 0; i < Scene->GetLevelSequencesCount(); ++i)
    {
        TSharedPtr<IDatasmithLevelSequenceElement> SeqElement = Scene->GetLevelSequence(i);
        if (SeqElement.IsValid())
        {
            FDatasmithLevelSequencePayload SeqPayload;
            Translator->LoadLevelSequence(SeqElement.ToSharedRef(), SeqPayload);
        }
    }
}
```

**文件路径解析**（翻译器内部使用的静态辅助方法）：

```cpp
// DatasmithNativeTranslator 提供了两个 protected 静态方法用于文件路径解析：
// ResolveFilePath - 将相对路径解析为绝对路径，搜索 ResourcePaths 列表
// ResolveSceneFilePaths - 遍历场景中所有元素，解析其引用的资源文件路径

// 这些方法在加载场景时自动调用，确保贴图、网格等资源引用能正确解析
FString ResolvedPath = FDatasmithNativeTranslator::ResolveFilePath(
    TEXT("Textures/MyTexture.png"), 
    ResourcePaths
);
```

## Demo 示例

一个自定义 Datasmith 翻译器的扩展示例：

```cpp
// MyCustomDatasmithTranslator.h
#pragma once

#include "DatasmithTranslator.h"

class FMyCustomDatasmithTranslator : public IDatasmithTranslator
{
public:
    virtual FName GetFName() const override { return TEXT("MyCustomTranslator"); }
    
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        OutCapabilities.bSupportsScene = true;
        OutCapabilities.bSupportsMeshes = true;
    }
    
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override
    {
        // 实现自定义场景加载逻辑
        // 例如从自定义格式解析场景层级、材质、网格等
        return true;
    }
    
    virtual bool LoadStaticMesh(
        const TSharedRef<IDatasmithMeshElement> MeshElement,
        FDatasmithMeshElementPayload& OutMeshPayload) override
    {
        // 实现自定义网格加载逻辑
        // 填充 OutMeshPayload 中的顶点、索引、法线、UV 等数据
        return true;
    }
    
    virtual bool LoadLevelSequence(
        const TSharedRef<IDatasmithLevelSequenceElement> LevelSequenceElement,
        FDatasmithLevelSequencePayload& OutLevelSequencePayload) override
    {
        // 实现自定义关卡序列加载逻辑
        return false; // 不支持时返回 false
    }
};
```

## 模块依赖

本模块属于大型插件 DatasmithImporter 的一个子模块，主要依赖同插件内的其他模块：

| 模块 | 用途 |
|---|---|
| `DatasmithTranslator` | 提供 `IDatasmithTranslator` 接口定义和 Datasmith 场景数据结构 |
| `DatasmithCore` | Datasmith 核心数据模型（IDatasmithScene、IDatasmithMeshElement 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到新的 UE_LOGF 宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. | 废弃带 bIncludeNestedObjects 参数的旧版对象遍历 API，适配引擎 API 变更 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，按要求用 PreEditChange/PostEditChange 包裹 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器开发工作 |

### 维护评价

**活跃维护中** ✅

- 自 2019 年创建以来持续维护，最近 3 个月内有多次更新
- 更新内容以引擎 API 适配和代码质量改进为主，说明模块跟随引擎版本同步演进
- 5.5 版本废弃了实验性的 Cloth 导入功能（`LoadCloth`），表明 Epic 在精简维护范围
- 作为 Enterprise 功能线的重要组件，Datasmith 是 Epic 商业化战略的一部分，预计长期维护
- `EnabledByDefault = false`，需手动启用，这与大多数 Enterprise 插件的策略一致

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests)