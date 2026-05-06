# InterchangeExport

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 导出模块 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `InterchangeExport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Export) | |

## 用途

`InterchangeExport` 是 Unreal Engine 5 Interchange 框架的导出模块。它提供了一个基础架构，用于将内存中的节点数据（如材质、纹理、静态网格体等）导出为外部文件格式。当前核心实现是 `UInterchangeTextureWriter`，它能够将 `FTextureNode` 类型的数据节点从 `UInterchangeBaseNodeContainer` 中批量导出为纹理文件。

该模块解决的是 **“资产导出标准化”** 问题：通过统一的基类 `UInterchangeWriterBase` 和容器 `UInterchangeBaseNodeContainer`，允许开发者自定义导出管线，而不需要直接操作具体的文件 I/O 细节。未来可扩展支持更多资源类型（如模型、动画等）。

## 使用场景

- **批量导出纹理资产**：当你需要将引擎内的纹理数据（如从导入管线生成）导出到磁盘时，使用 `UInterchangeTextureWriter`。
- **自定义导出管线**：如果你需要移植到非标准格式（如自定义 `.ctexture`），可以继承 `UInterchangeWriterBase` 并注册到 Interchange 框架。
- **编辑器/自动化工具**：在自动化批处理或自定义编辑器工具中，通过拦截导出事件使用本模块。

## 蓝图用法

`UInterchangeTextureWriter` 标记为 `BlueprintType`，但所有公开的成员函数均为 `virtual` 且没有 `UFUNCTION(BlueprintCallable)` 标记，因此**不能在蓝图中直接调用**。需要在 C++ 中完成导出操作，或通过蓝图调用 C++ 封装的辅助函数。

若需要在蓝图中触发导出，通常的做法是编写一个 `BlueprintCallable` 的自定义函数，内部调用 `UInterchangeTextureWriter::Export()`。

### 核心节点

由于本模块没有暴露任何蓝图可调用节点，暂不列表。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeTextureWriter.h"
#include "Nodes/InterchangeBaseNodeContainer.h"
```

### 基本用法

从 `InterchangeTextureWriter.h` 中的声明可以得知，使用时需要创建一个 `UInterchangeTextureWriter` 实例，并传入一个填充好纹理节点的 `UInterchangeBaseNodeContainer`。

```cpp
// 创建节点容器并填充纹理节点（示例：仅示意结构，实际填充需遍历导入结果）
UInterchangeBaseNodeContainer* Container = NewObject<UInterchangeBaseNodeContainer>();
// ... 添加 FTextureNode 到 Container 中（省略细节） ...

// 创建导出器并执行导出
UInterchangeTextureWriter* TextureWriter = NewObject<UInterchangeTextureWriter>();
bool bSuccess = TextureWriter->Export(Container);

// 检查结果
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Texture export succeeded."));
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Texture export failed."));
}
```

> **注意**：`Export()` 的返回类型为 `bool`，但具体导出的文件路径和目标格式由 `Container` 中的节点属性决定，当前版本未公开详细路径设置方式。

### 进阶用法

结合 Interchange 框架的整个导入管线，可以在导入后自动触发导出。以下是一个从 `InterchangeImport` 模块获取容器并导出的伪代码：

```cpp
// 假设已通过 InterchangeImport 模块加载了一个文件，获得了节点容器
UInterchangeBaseNodeContainer* ImportedContainer = ...; // 来自导入过程

// 过滤出所有纹理节点（需要自定义过滤逻辑，因为当前 Export 仅处理 FTextureNode）
UInterchangeBaseNodeContainer* FilteredContainer = NewObject<UInterchangeBaseNodeContainer>();
ImportedContainer->IterateNodesOfType<UInterchangeTextureNode>([&](UInterchangeTextureNode* TextureNode)
{
    // 复制纹理节点到新容器
    FilteredContainer->AddNode(TextureNode);
});

// 导出过滤后的纹理
UInterchangeTextureWriter* Writer = NewObject<UInterchangeTextureWriter>();
Writer->Export(FilteredContainer);
```

## Demo 示例

一个可编译的最小示例，演示如何创建 `UInterchangeTextureWriter` 并导出纹理（假设已经有一个包含纹理节点的容器）。

### MyExportActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyExportActor.generated.h"

UCLASS()
class MYPROJECT_API AMyExportActor : public AActor
{
    GENERATED_BODY()

public:
    // 在编辑器中调用，导出所有纹理
    UFUNCTION(BlueprintCallable, Category = "Export")
    void ExportAllTextures();

    // 指向节点容器的指针（可从导入管线获取）
    UPROPERTY()
    UInterchangeBaseNodeContainer* TextureContainer;
};
```

### MyExportActor.cpp

```cpp
#include "MyExportActor.h"
#include "InterchangeTextureWriter.h"
#include "Nodes/InterchangeBaseNodeContainer.h"

void AMyExportActor::ExportAllTextures()
{
    if (!TextureContainer)
    {
        UE_LOG(LogTemp, Warning, TEXT("TextureContainer is null. Cannot export."));
        return;
    }

    UInterchangeTextureWriter* Writer = NewObject<UInterchangeTextureWriter>(this);
    bool bSuccess = Writer->Export(TextureContainer);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Texture export completed successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Texture export failed."));
    }
}
```

## 模块依赖

由于未提供 `InterchangeExport.Build.cs` 内容，根据代码实际使用的头文件推断依赖：

| 模块 | 用途 |
|---|---|
| `InterchangeNodes` | 使用 `UInterchangeBaseNodeContainer` 和纹理节点类型 |
| `InterchangeCommon` | 基础类型定义（如 `INTERCHANGEEXPORT_API` 宏） |

以上两个模块为 Interchange 框架的基础组件，通常已经自动引入。其他依赖（如 `Core`, `CoreUObject`, `Engine`）为标准项，此处省略。

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` — Fixed editor hanging when level reimporting a file containing skeletal meshes（修复包含骨骼网格体的文件重新导入时编辑器挂起）
- 2025-10-23 `0158cf6a` — [Interchange] Removing unintended LOD specialization from named LOD Groups. （移除命名LOD组中意外的LOD特化）
- 2025-10-21 `63c630c0` — [Interchange] Fixing missing animation sequence import for LevelSequence on StaticMesh imported with （修复静态网格体导入时LevelSequence缺失动画序列）
- 2025-10-17 `765b3a10` — Fixed compilation error with NonUnity InterchangeWorker（修复非Unity编译错误）
- 2025-10-17 `2c91170f` — Replaced use of /InterchangeAssets/Materials/PhongSurfaceMaterial with /Interch……（替换材质引用路径）

### 维护评价

- **创建时间**：2025-10-17（约3个月）
- **最近更新**：2025-12-18（不到1个月前），仍有活跃的 bug 修复
- **活跃度**：Interchange 框架作为 UE5 的新一代导入导出系统，处于积极开发阶段，近期更新频繁
- **已知问题**：当前模块仅提供纹理导出功能，其他资源类型的导出尚未公开
- **推荐使用**：✅ 推荐。作为 Interchange 官方提供的导出模块，适用于需要标准化导出管线的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Export)
- [官方文档（暂无）]()
- [Interchange 框架概览](https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-framework)