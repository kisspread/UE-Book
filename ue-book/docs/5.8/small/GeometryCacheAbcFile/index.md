# Geometry Cache from Alembic File (Experimental)

> Support Geometry Cache from Alembic file without importing

| 属性 | 值 |
|---|---|
| 中文名 | Alembic 文件几何缓存 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCacheAbcFile` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-02-03 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCacheAbcFile) | |

## 用途

这个插件提供了一种**轻量级、无需预先导入**的方式来直接使用 Alembic (`.abc`) 文件作为几何缓存数据源。它解决了需要快速预览或使用 Alembic 动画网格数据，而不希望执行完整导入流程（包括资产创建、烘焙等）的场景。插件在运行时直接读取 Alembic 文件，并为引擎的 `GeometryCache` 系统提供数据。

## 使用场景

- **快速原型迭代**：美术师导出 Alembic 文件后，希望立即在引擎中查看动画效果，无需等待漫长的导入和资产处理过程。
- **数据流式传输**：处理极大的 Alembic 文件，只在需要时从磁盘读取特定帧的数据，减少内存占用。
- **外部修改支持**：当 Alembic 文件在外部软件中被修改后，可以在编辑器中重新加载，立即看到更新，无需重新导入。

## 蓝图用法

### 核心节点

插件主要通过组件暴露给蓝图。在场景中放置 `GeometryCacheAbcFileComponent` 或 `GeometryCacheAbcFileActor`。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AlembicFilePath` (属性) | 指定要加载的 `.abc` 文件路径 | `UGeometryCacheAbcFileComponent` |
| `SamplingSettings` (属性) | 控制动画采样参数 | `UGeometryCacheAbcFileComponent` |
| `ConversionSettings` (属性) | 控制几何体转换参数 | `UGeometryCacheAbcFileComponent` |
| `GeometryCacheSettings` (属性) | 控制几何缓存特定设置 | `UGeometryCacheAbcFileComponent` |
| `ReloadAbcFile` | 重新加载指定的 Alembic 文件 | `UGeometryCacheAbcFileComponent` |

### 使用示例（蓝图描述）

1.  在蓝图中，使用 `Spawn Actor From Class` 节点生成一个 `AGeometryCacheAbcFileActor`。
2.  获取其 `GeometryCacheAbcFileComponent` 组件引用。
3.  在组件的 `Details` 面板中，设置 `Alembic FilePath` 属性指向你的 `.abc` 文件。
4.  调整 `SamplingSettings`、`ConversionSettings` 等属性以控制导入行为。
5.  若需要重新加载文件（例如文件在外部被修改），可调用 `ReloadAbcFile` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheAbcFileComponent.h"
#include "GeometryCacheTrackAbcFile.h"
```

### 基本用法

以下示例展示如何在 C++ 中动态创建一个使用指定 Alembic 文件的几何缓存轨道。思路是构建一个临时的 `UGeometryCache` 资产和轨道。
*来源：基于 `UGeometryCacheAbcFileComponent::InitializeGeometryCache` 逻辑简化*

```cpp
// 假设 AbcFilePath 是一个有效的 .abc 文件路径
FString AbcFilePath = TEXT("/Game/MyAnimation.abc");

// 1. 创建一个临时的、内存中的 GeometryCache 资产
UPackage* TempPackage = NewObject<UPackage>(nullptr, TEXT("/Temp/TransientGeometryCache"), RF_Transient);
UGeometryCache* TempGeometryCache = NewObject<UGeometryCache>(TempPackage, TEXT("TempGeometryCache"), RF_Transient);

// 2. 创建并配置 Alembic 导入设置（可选，有默认值）
UAbcImportSettings* AbcSettings = NewObject<UAbcImportSettings>(GetTransientPackage());

// 3. 创建轨道对象并设置源文件
UGeometryCacheTrackAbcFile* AbcTrack = NewObject<UGeometryCacheTrackAbcFile>(TempGeometryCache);
bool bSuccess = AbcTrack->SetSourceFile(AbcFilePath, AbcSettings);
if (bSuccess)
{
    // 4. 将轨道添加到缓存中，并设置材质
    TempGeometryCache->Tracks.Add(AbcTrack);
    AbcTrack->SetupGeometryCacheMaterials(TempGeometryCache);

    // 5. (可选) 将此缓存赋值给某个 UGeometryCacheComponent 以进行播放
    // MyCacheComponent->SetGeometryCache(TempGeometryCache);
}
```

### 进阶用法

直接访问轨道对象来查询网格数据，适用于需要精细控制数据读取的场景。
*来源：基于 `UGeometryCacheTrackAbcFile` 的公开接口*

```cpp
UGeometryCacheTrackAbcFile* Track = ...; // 获取有效的轨道对象
int32 SampleIndex = 0; // 要查询的帧索引

// 查询指定帧的网格数据
FGeometryCacheMeshData MeshData;
if (Track->GetMeshData(SampleIndex, MeshData))
{
    // 成功获取到该帧的顶点、索引等数据，可用于自定义渲染或处理
    UE_LOG(LogTemp, Log, TEXT("Frame %d has %d vertices."), SampleIndex, MeshData.Positions.Num());
}

// 检查两帧之间的拓扑结构是否兼容（例如，是否可以插值）
bool bCompatible = Track->IsTopologyCompatible(0, 10);
```

## Demo 示例

一个最小的可运行示例，展示如何创建 `AGeometryCacheAbcFileActor` 并加载文件。
*注意：你需要确保插件已启用。*

```cpp
// MyAbcDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAbcDemoActor.generated.h"

UCLASS()
class AMyAbcDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAbcDemoActor();

    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UGeometryCacheAbcFileComponent> AbcCacheComponent;

    // 指定在编辑器中或代码里设置的 .abc 文件路径
    UPROPERTY(EditAnywhere, Category="Demo")
    FFilePath MyAbcFile;
};
```

```cpp
// MyAbcDemoActor.cpp
#include "MyAbcDemoActor.h"
#include "GeometryCacheAbcFileComponent.h"

AMyAbcDemoActor::AMyAbcDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建组件
    AbcCacheComponent = CreateDefaultSubobject<UGeometryCacheAbcFileComponent>(TEXT("AbcCache"));
    RootComponent = AbcCacheComponent;
}

void AMyAbcDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 如果在编辑器中指定了文件路径，BeginPlay 时组件会自动加载。
    // 这里演示如何在运行时动态加载。
    if (!MyAbcFile.FilePath.IsEmpty())
    {
        AbcCacheComponent->AlembicFilePath = MyAbcFile;
        AbcCacheComponent->ReloadAbcFile();
    }
}
```

## 模块依赖

使用此插件前，你的模块的 `Build.cs` 文件需要添加对以下**特殊模块**的依赖：

| 模块 | 用途 |
|---|---|
| `GeometryCacheAbcFile` | 插件的核心模块，提供组件和轨道功能。 |
| `GeometryCache` | 几何缓存的基础框架，提供 `UGeometryCacheComponent` 等基类。 |
| `AlembicImporter` | 提供 Alembic 文件解析和导入的底层功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 新式写法。 |
| 2025-11-03 | `2dd15934` | GeometryCacheAbcFile: Migrate to the UE5 DDC API | 迁移至 UE5 的派生数据缓存 (DDC) API。 |
| 2023-08-22 | `058843c9` | [GeomCache] Added some virtual method to the tracks to sample at a specific frame directly (sample i | 为轨道类添加了直接按帧采样的虚函数。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件范围的更新或修复。 |
| 2023-01-06 | `8fd10b0e` | Dependency cleanup around some Rendering headers. | 清理了与渲染头文件相关的依赖关系。 |

### 维护评价

该插件自 2020 年创建，属于**实验性功能**，且**默认未启用**。从更新历史看，它仍然**被维护**，例如在 2025 年底进行了针对 UE5 DDC API 的重要迁移。更新频率不算高，但近年来仍有功能性改动。它作为一个特定用途的工具存在，适合有“直接使用 Alembic 文件而不导入”需求的用户。但需注意其实验性状态，可能在未来有变动或不兼容更新。**推荐**在相关需求明确且能接受其限制时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCacheAbcFile)
- [官方文档]() （无）
- [测试用例]() （未在插件目录内发现标准测试用例）