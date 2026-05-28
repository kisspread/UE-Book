# Datasmith External Source

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 外部数据源 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithExternalSource) | |

## 用途

`DatasmithExternalSource` 模块是 Datasmith 插件的基础设施之一，其核心功能是**管理和提供对外部数据源的统一访问接口**。它解决了如何从不同来源（如本地 `.udatasmith` 文件或通过 DirectLink 协议的实时流）获取 Datasmith 场景数据的问题。

通过定义 `FExternalSource` 基类和一系列具体的实现（如 `FDatasmithFileExternalSource` 和 `FDatasmithDirectLinkExternalSource`），本模块实现了：
1.  **统一抽象**：为上层应用（如 `DatasmithImporter` 模块）提供一致的接口来获取 `IDatasmithScene`，而无需关心数据是来自文件还是网络流。
2.  **实时连接**：通过集成 DirectLink，支持从 CAD/BIM 软件实时接收场景更新，避免了传统的文件导出-导入中间步骤。
3.  **URI 解析**：通过 `IUriResolver` 接口，支持使用 `directlink://` 或 `file://` 等 URI 方案来定位数据源。

简单来说，它是 Datasmith 生态系统的“数据连接层”，让 UE 能够灵活地接入来自各种设计软件的三维数据。

## 使用场景

*   **实时设计评审**：建筑师或设计师在 SketchUp、Revit 或 3ds Max 中修改模型时，通过 DirectLink 协议，UE 中的可视化场景可以实时同步更新，无需手动导出和重新导入文件。
*   **自动化数据流水线**：在需要自动化处理 Datasmith 数据的程序或工具中，通过代码直接解析 `file://` 或 `directlink://` URI，自动加载和获取场景数据。
*   **扩展数据源**：开发者可以继承 `FExternalSource` 类，创建自定义的数据源解析器，例如从特定的数据库或网络服务中加载 Datasmith 格式的场景。

## 蓝图用法

本模块（`DatasmithExternalSource`）主要提供底层运行时支持，其公开的蓝图可调用 API 较少，更多是为 `DatasmithImporter` 等上层模块提供服务。在蓝图中使用 Datasmith 功能，通常是通过 `DatasmithImporter` 模块提供的节点（如“导入 Datasmith 场景”）来完成，这些节点内部会调用本模块的数据源管理功能。

因此，**直接使用本模块的蓝图节点进行高级定制的场景较少**。其价值主要体现在 C++ 层面的扩展和底层架构中。

## C++ 用法

本模块的主要用法体现在对已有框架的扩展和底层接口的调用。

### 头文件引入

```cpp
#include "DatasmithExternalSourceModule.h" // 模块访问
#include "IExternalSource.h" // 数据源基类接口（来自 ExternalSource 模块）
```

### 基本用法：获取模块状态

```cpp
#include "DatasmithExternalSourceModule.h"

// 检查 DatasmithExternalSource 模块是否已加载并可用
if (FDatasmithExternalSourceModule::IsAvailable())
{
    // 模块已加载，可以安全地访问其功能
    UE_LOG(LogTemp, Log, TEXT("DatasmithExternalSource module is available."));
}
```
*代码基于模块管理类 `FDatasmithExternalSourceModule` 的典型用法。*

### 进阶用法：创建自定义数据源

通过继承 `FExternalSource` 并注册 URI 解析器，可以创建自定义数据源。

```cpp
// MyCustomExternalSource.h
#pragma once

#include "IExternalSource.h"

class FMyCustomExternalSource : public FExternalSource
{
public:
    explicit FMyCustomExternalSource(const FSourceUri& InSourceUri)
        : FExternalSource(InSourceUri)
    {}

    // 实现数据源的核心接口
    virtual FString GetSourceName() const override;
    virtual bool IsAvailable() const override;
    // ... 其他 FExternalSource 虚函数实现

    // 通常还需要实现获取具体数据的方法
    // virtual TSharedPtr<IDatasmithScene> LoadScene() = 0;
};
```

```cpp
// MyUriResolver.h
#pragma once

#include "IUriResolver.h"

class FMyUriResolver : public IUriResolver
{
public:
    virtual bool CanResolveUri(const FSourceUri& URI) const override
    {
        // 识别自定义的 URI 方案
        return URI.GetScheme() == TEXT(“mycustom”);
    }

    virtual TSharedPtr<FExternalSource> GetOrCreateExternalSource(const FSourceUri& URI) const override
    {
        return MakeShared<FMyCustomExternalSource>(URI);
    }
    // ... 其他接口实现
};
```

在 `StartupModule()` 中，将自定义解析器注册到模块的 URI 解析器列表中。
*思路基于 `FDatasmithFileUriResolver` 的实现模式。*

## Demo 示例

以下是一个最小化的自定义 `FExternalSource` 实现，用于从内存字符串（模拟）中加载 Datasmith 场景。

```cpp
// SimpleMemoryExternalSource.h
#pragma once

#include "IExternalSource.h"

class IDatasmithScene;

class FSimpleMemoryExternalSource : public FExternalSource
{
public:
    explicit FSimpleMemoryExternalSource(const FSourceUri& InSourceUri, const FString& InSceneJson)
        : FExternalSource(InSourceUri)
        , SceneJson(InSceneJson)
    {}

    virtual ~FSimpleMemoryExternalSource() = default;

    virtual FString GetSourceName() const override { return TEXT(“MemorySource”); }
    virtual bool IsAvailable() const override { return true; } // 内存数据总是可用
    virtual FMD5Hash GetSourceHash() const override
    {
        // 简单地对内容字符串计算哈希
        return FMD5Hash::HashString(*SceneJson);
    }

    // 此示例中，我们将加载操作设计为同步的，实际应异步
    virtual TSharedPtr<IDatasmithScene> GetDatasmithScene() const override
    {
        // 注意：实际场景应使用 Datasmith 的解析器从 SceneJson 构建 IDatasmithScene
        // 此处仅为示意，返回空指针。
        return nullptr;
    }

protected:
    // 通常由 GetDatasmithScene 或异步加载函数内部调用
    TSharedPtr<IDatasmithScene> LoadImpl()
    {
        // 调用 Datasmith 的 JSON/数据解析器
        // FDatasmithSceneUtils::CreateSceneFromJson(SceneJson);
        return nullptr; // 示例返回
    }

private:
    FString SceneJson;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | 提供 `IDatasmithScene` 等核心数据接口 |
| `DirectLink` | 实现 DirectLink 网络协议，用于实时数据接收 |
| `ExternalSource` | 提供 `FExternalSource`、`IUriResolver` 等基类接口 |

**省略常见依赖**：仅列出该插件独特依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数导致的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF，可能是日志格式或分类的标准化。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了带 `bIncludeNestedObjects` 参数的 `GetObjects`/`ForEachObjectWithOuter` 函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了在 `PreEditChange`/`PostEditChange` 中修改纹理属性的代码，使其符合规范。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 开展了新材质翻译器的相关工作。 |

### 维护评价

*   **活跃维护**：最近一次更新在 2026 年 5 月，且近半年内有多次提交，涉及代码清理、API 更新和功能工作，表明该模块仍在被积极维护。
*   **状态稳定**：虽然插件本身创建于约 7 年前，但作为企业版 Datasmith 工具链的关键基础设施，其稳定性和持续维护至关重要。从提交历史看，团队在持续优化和适配 UE 的更新。
*   **推荐使用**：**是**。对于需要接入 Datasmith 数据流（特别是实时数据）的项目或工具开发，本模块是必不可少的底层组件。它提供了稳定、可扩展的数据源抽象层。

## 相关链接

- [源码 (DatasmithExternalSource 模块)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithExternalSource)
- [Datasmith 整体源码 (插件根目录)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档 (Datasmith 概览)](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)