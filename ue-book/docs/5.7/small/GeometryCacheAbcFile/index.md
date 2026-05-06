# Geometry Cache from Alembic File(Experimental)

> Support Geometry Cache from Alembic file without importing

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存Alembic文件 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCacheAbcFile` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCacheAbcFile) | |

## 用途

该插件允许在编辑器中**直接**使用 Alembic（.abc）文件作为几何缓存（Geometry Cache），无需事先导入或转换。它通过运行时加载文件并实时解码网格数据，实现与导入的几何缓存相同的播放、渲染和交互功能。适用于需要快速预览外部动画资源或动态加载内容的工作流，例如角色动画、布料模拟或特效预览。

## 使用场景

- 你从 DCC 工具（Maya、Blender）导出 Alembic 动画，希望不经过导入直接放入关卡预览或测试。
- 你需要频繁迭代 Alembic 文件内容，每次修改后只需重新加载文件即可更新场景，避免重复导入。
- 项目需要动态加载外部缓存文件（例如用户自定义上传的动画），插件提供了在编辑器中直接引用的能力。

## 蓝图用法

插件主要提供 `UGeometryCacheAbcFileComponent` 组件，可在蓝图中放置和配置。该组件继承自 `UGeometryCacheComponent`，因此支持所有几何缓存的标准功能（如播放、暂停、循环）。

### 核心属性（BlueprintReadWrite）

| 属性 | 说明 | 类型 |
|---|---|---|
| `AlembicFilePath` | 指定要加载的 Alembic 文件路径（仅编辑器可见） | `FFilePath` |
| `SamplingSettings` | 帧采样设置（帧范围、采样频率等） | `FAbcSamplingSettings` |
| `ConversionSettings` | 单位、旋转轴转换设置 | `FAbcConversionSettings` |
| `GeometryCacheSettings` | 几何缓存生成参数（如是否合并网格、是否优化索引） | `FAbcGeometryCacheSettings` |
| `NormalGenerationSettings` | 法线生成策略（是否强制重新计算法线） | `FAbcNormalGenerationSettings` |
| `MaterialSettings` | 材质导入相关设置（如颜色映射） | `FAbcMaterialSettings` |

### 使用示例（蓝图）

1. **在关卡中创建 Alembic 几何缓存 Actor**  
   使用“放置Actor”面板搜索 `GeometryCacheAbcFileActor`（或通过内容浏览器右键菜单添加），该 Actor 会自动包含 `GeometryCacheAbcFileComponent`。

2. **配置文件路径**  
   选中 Actor 后，在细节面板中找到 `Alembic File Path` 属性，选择 `.abc` 文件。组件会自动加载并播放。

3. **控制播放**  
   由于组件继承自 `GeometryCacheComponent`，你可以通过蓝图节点 `Play`、`Stop`、`SetLooping` 等控制播放。

### 注意

- 所有 Alembic 相关设置（采样、转换、几何体）均在组件细节面板中暴露，无需额外蓝图节点。
- 细节面板中提供了 **Reload Abc File** 按钮，用于手动重新加载文件（开发调试用）。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheAbcFileComponent.h"
#include "GeometryCacheAbcFileActor.h"
```

### 基本用法

```cpp
// 在关卡中生成一个 Alembic 几何缓存 Actor
AGeometryCacheAbcFileActor* AbcActor = World->SpawnActor<AGeometryCacheAbcFileActor>(AGeometryCacheAbcFileActor::StaticClass(), SpawnTransform);

// 获取组件并设置 Alembic 文件路径（相对 Content 目录）
UGeometryCacheAbcFileComponent* AbcComponent = AbcActor->GetComponentByClass<UGeometryCacheAbcFileComponent>();
AbcComponent->AlembicFilePath.FilePath = TEXT("/Game/MyAnimations/Character.abc");

// 调用 ReloadAbcFile 以加载新路径
AbcComponent->ReloadAbcFile();

// 播放
AbcComponent->Play();
```

### 进阶用法

```cpp
// 直接在现有 Actor 上添加组件
UGeometryCacheAbcFileComponent* NewComp = NewObject<UGeometryCacheAbcFileComponent>(MyActor);
NewComp->RegisterComponent();
NewComp->AlembicFilePath.FilePath = TEXT("/Game/Data/Cloth.abc");
NewComp->ReloadAbcFile(); // 加载文件
NewComp->SetLooping(true);
NewComp->Play();
```

> **注意**：`ReloadAbcFile()` 会触发内部重新创建几何缓存 Track 和流式数据。文件路径必须在调用前设置。

## Demo 示例

以下是一个可编译的最小 C++ 示例，用于在运行时动态创建并播放 Alembic 几何缓存。

### GeometryCacheAbcFileDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeometryCacheAbcFileDemo.generated.h"

class UGeometryCacheAbcFileComponent;

UCLASS()
class AGemoetryCacheAbcFileDemo : public AActor
{
    GENERATED_BODY()

public:
    AGemoetryCacheAbcFileDemo();

    UPROPERTY(EditAnywhere, Category = "Alembic")
    FString AlembicFilePath;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UGeometryCacheAbcFileComponent* AbcComponent;
};
```

### GeometryCacheAbcFileDemo.cpp

```cpp
#include "GeometryCacheAbcFileDemo.h"
#include "GeometryCacheAbcFileComponent.h"

AGemoetryCacheAbcFileDemo::AGemoetryCacheAbcFileDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    AbcComponent = CreateDefaultSubobject<UGeometryCacheAbcFileComponent>(TEXT("AbcComponent"));
    AbcComponent->SetupAttachment(RootComponent);
}

void AGemoetryCacheAbcFileDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!AlembicFilePath.IsEmpty())
    {
        AbcComponent->AlembicFilePath.FilePath = AlembicFilePath;
        AbcComponent->ReloadAbcFile();
        AbcComponent->Play();
    }
}
```

## 模块依赖

要使用该插件，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AlembicImporter` | 提供 Alembic 文件解析和导入核心（`FAbcFile`） |
| `GeometryCache` | 提供几何缓存基础组件、轨道和渲染路径 |
| `AbcImportSettings` | 提供采样、转换、几何体等设置结构体（通常由 AlembicImporter 引入） |

**示例 `Build.cs` 片段**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "AlembicImporter",
    "GeometryCache",
    // 标准模块（Core、Engine等自动依赖）
});
```

## 维护状态

### 近期更新

| 日期 | Commit | 解读 |
|---|---|---|
| 2023-08-22 | `058843c9` | 为轨道添加虚拟方法以直接采样指定帧（优化性能） |
| 2023-01-16 | `bbc37aa2` | 插件根目录结构调整 |
| 2023-01-06 | `8fd10b0e` | 渲染头文件依赖清理 |
| 2022-11-03 | `fa90b399` | 为未来改动添加必要的 include |
| 2022-10-26 | `5298cc81` | 非 Unity 编译修复（插件初始创建） |

### 维护评价

- 创建于 2022 年 10 月，至今约 2 年。
- 最近一次实质性更新为 2023 年 8 月（添加帧直接采样接口），之后超过 1 年没有代码改动。
- 插件标记为 **实验性（IsBetaVersion=true）**，默认未启用。
- 目前无已知严重限制，但功能较为基础，缺乏运行时烘焙或优化选项。
- **建议**：适合编辑器和开发环境快速预览 Alembic 内容，不推荐用于发布产品，除非经充分测试。如需稳定运行时缓存，建议使用标准 Geometry Cache 导入流程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCacheAbcFile)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/geometry-cache-abc-file-plugin-in-unreal-engine/)（UE 5.3 后新增，可参考）