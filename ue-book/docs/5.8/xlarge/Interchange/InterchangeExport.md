# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（管线配置资产） |
| 模块 | `InterchangeCommon` (Runtime), `InterchangeNodes` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeExport` (Runtime), `InterchangePipelines` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeMessages` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `InterchangeAnalytics` (Runtime), `GLTFCore` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 约 2022（官方未公开） |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange) | |

---

## 用途

Interchange 是 UE5 的下一代资产导入/导出框架，旨在取代旧版 `FReimportManager` + `UFactory` 的粗粒度导入管线。它将资产导入过程拆分为三个可插拔阶段：

1. **Parser（解析器）**：将外部文件（FBX、glTF 等）解析为通用的 `UInterchangeBaseNode` 节点图
2. **Pipeline（管线）**：对节点图执行转换、过滤、属性映射等操作
3. **Factory（工厂）**：将处理后的节点图创建为 UE 资产

**本模块 `InterchangeExport`** 负责反向路径——将 UE 资产**导出**为外部格式。它提供 `UInterchangeWriterBase` 基类和一系列 Writer 实现（如 `UInterchangeTextureWriter`），将资产序列化回节点图，再由管线输出为文件。

这个框架存在的核心原因是：旧的 UFactory 体系缺乏管线化处理能力，难以扩展、难以复用中间数据。Interchange 通过节点图作为统一中间表示，让导入和导出共享同一套数据模型。

---

## 使用场景

- 你项目需要批量导入大量 FBX/glTF 资产，且需要自定义导入规则（如自动设置 LOD、压缩格式）→ 用 Interchange Pipeline 在导入时批量处理
- 你需要将 UE 资产导出为外部格式（如纹理导出为 PNG）→ 用 InterchangeExport 的 Writer 体系
- 你要支持一种新的 3D 格式 → 编写自定义 Parser 模块接入 Interchange 框架
- 你希望导入过程可异步执行、不阻塞编辑器 → Interchange Dispatcher 提供异步调度

---

## 蓝图用法

`UInterchangeTextureWriter` 标记了 `BlueprintType`，可在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Export` | 将 BaseNodeContainer 中的所有纹理节点导出 | `UInterchangeTextureWriter` |

> **注意**：`UInterchangeTextureWriter` 同时标记了 `Experimental`，API 可能在后续版本变动。

### 使用示例（蓝图描述）

1. 创建一个 `UInterchangeTextureWriter` 对象
2. 获取或构建一个 `UInterchangeBaseNodeContainer`（包含你要导出的纹理节点）
3. 调用 `Export` 节点，传入 NodeContainer
4. Writer 会遍历所有 FTextureNode 并执行导出

---

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "InterchangeExportModule.h"

// 纹理导出 Writer（Experimental）
#include "InterchangeTextureWriter.h"
```

### 基本用法：获取导出模块

```cpp
// 检查模块是否可用（避免在模块未加载时崩溃）
if (IInterchangeExportModule::IsAvailable())
{
    // 获取模块单例
    IInterchangeExportModule& ExportModule = IInterchangeExportModule::Get();
}
```

> 来源：`Public/InterchangeExportModule.h`

### 基本用法：导出纹理

```cpp
#include "InterchangeExportModule.h"
#include "InterchangeTextureWriter.h"
#include "InterchangeBaseNodeContainer.h"

// 创建纹理 Writer
UInterchangeTextureWriter* TextureWriter = NewObject<UInterchangeTextureWriter>();

// 准备节点容器（节点由导入阶段或手动构建）
UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();

// 执行导出
bool bSuccess = TextureWriter->Export(NodeContainer);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("纹理导出成功"));
}
```

> 来源：`Public/InterchangeTextureWriter.h`

### 进阶用法：自定义 Writer

继承 `UInterchangeWriterBase` 实现自定义资产导出器：

```cpp
#include "InterchangeWriterBase.h"

UCLASS()
class UMyCustomMeshWriter : public UInterchangeWriterBase
{
    GENERATED_BODY()

public:
    // Export 返回 true 表示 Writer 能处理该 NodeContainer 中的节点
    virtual bool Export(UInterchangeBaseNodeContainer* BaseNodeContainer) const override
    {
        // 遍历容器中的 StaticMesh 节点
        // 读取顶点、索引、材质引用等属性
        // 序列化为自定义格式
        return true;
    }
};
```

---

## Demo 示例

一个完整的自定义纹理导出 Writer 示例：

```cpp
// MyTextureExportWriter.h
#pragma once

#include "CoreMinimal.h"
#include "InterchangeTextureWriter.h"
#include "MyTextureExportWriter.generated.h"

/**
 * 自定义纹理导出 Writer：将纹理节点导出为指定格式
 */
UCLASS(MinimalAPI)
class UMyTextureExportWriter : public UInterchangeTextureWriter
{
    GENERATED_BODY()

public:
    virtual bool Export(UInterchangeBaseNodeContainer* BaseNodeContainer) const override;
};
```

```cpp
// MyTextureExportWriter.cpp
#include "MyTextureExportWriter.h"

bool UMyTextureExportWriter::Export(UInterchangeBaseNodeContainer* BaseNodeContainer) const
{
    if (!BaseNodeContainer)
    {
        return false;
    }

    // 调用父类实现处理标准纹理导出
    bool bResult = Super::Export(BaseNodeContainer);

    // 可在此添加自定义后处理逻辑
    // 例如：记录导出日志、生成缩略图等
    UE_LOG(LogTemp, Log, TEXT("UMyTextureExportWriter: 导出完成, 结果=%s"),
        bResult ? TEXT("成功") : TEXT("失败"));

    return bResult;
}
```

---

## 模块依赖

InterchangeExport 模块的依赖关系（基于类继承推断）：

| 模块 | 用途 |
|---|---|
| `InterchangeCommon` | 通用类型定义、节点基类 |
| `InterchangeNodes` | 具体节点类型（如 FTextureNode） |
| `InterchangeFactoryNodes` | 工厂节点，定义资产创建逻辑 |
| `InterchangePipelines` | 管线处理，Writer 需要与管线协作 |

> 由于 `InterchangeExport.Build.cs` 未在源码中展示，以上依赖基于 `UInterchangeWriterBase` 和 `UInterchangeBaseNodeContainer` 的头文件引用推断。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | USD 预生成：实现骨骼和物理资产的追踪 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 的本地化警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重导入时重置已有 LOD 模型，更新骨骼绑定和映射 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复 uFBX 解析器为实验性功能 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复导入对象列表中空指针导致的崩溃 |

> 注：以上 commit 来自整个 Interchange 插件目录，不仅限于 Export 模块。

### 维护评价

- **维护状态**：🟢 **活跃维护** — Epic 持续投入，每周都有功能性更新和 Bug 修复
- **创建时间**：约 2022 年（随 UE5 发布引入），生命周期约 4 年
- **当前定位**：作为 UE5 官方推荐的资产导入/导出框架，正在逐步替代旧的 UFactory 体系
- **已知限制**：
  - `UInterchangeTextureWriter` 仍标记为 `Experimental`，API 可能变动
  - FBX 解析器刚被恢复为实验性（`3cfa4417`），说明其稳定性仍在验证中
  - 从 recent commits 可见，重导入（reimport）流程仍有边界情况需要修复
- **推荐程度**：⭐⭐⭐⭐ **推荐使用** — 作为 Epic 官方力推的框架，适合新项目采用；对于已有大量 UFactory 自定义代码的项目，建议评估迁移成本后再决定

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange)
- [导出模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Export)
- 官方文档：暂无（.uplugin 中 DocsURL 为空）