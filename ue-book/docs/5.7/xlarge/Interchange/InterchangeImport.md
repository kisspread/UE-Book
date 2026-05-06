# Interchange Import

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交互框架导入模块 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Interchange/Runtime) | |

> ⚠️ 注意：该插件仍处于 Beta 阶段（`IsBetaVersion` 为 `true`），API 可能存在变动。

## 用途

`InterchangeImport` 是 Interchange 框架中负责实际导入逻辑的核心运行时模块。它解析多种格式的源文件（FBX、GLTF、音频、MaterialX 等），将其转换为引擎内部表示并最终生成 UE 资产。

该模块解决了以下问题：
- 从多种外部文件格式（FBX、GLTF、WAV、MP3 等）导入静态网格体、骨骼网格体、动画、材质、音频、关卡序列等资产。
- 通过可扩展的管道（Pipelines）机制，允许用户自定义导入后的处理逻辑（例如重命名、材质替换、LOD 设置等）。
- 支持 MaterialX 材质图的完整翻译，包括自定义着色器节点。

## 使用场景

- **导入 FBX/GLTF 模型**：将外部 3D 模型（含动画）导入 UE，引擎自动调用 `InterchangeImport` 解析。
- **导入音频文件**：支持 WAV、OGG、MP3、FLAC、OPUS 等常见音频格式。
- **导入 MaterialX 材质包**：在材质编辑器中直接使用 MaterialX 标准材质。
- **自定义导入管道**：通过继承 `UInterchangePipeline` 在导入时执行自定义逻辑（例如自动生成碰撞体）。

## 蓝图用法

Interchange 导入流程主要通过编辑器 UI 和 C++ 对接，蓝图可直接操作 **Interchange 工厂节点**和**管道**。

### 核心节点

`InterchangeImport` 模块本身不暴露 BlueprintCallable 函数，但 Interchange 框架提供了以下蓝图可访问的类：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Asset` | 启动导入操作（编辑器可用） | `UInterchangeManager` |
| `Create Pipeline` | 创建自定义导入管道 | `UInterchangePipeline` |
| `Get Result Assets` | 获取导入结果资产数组 | `UInterchangeResultsContainer` |

**使用示例**（蓝图描述）：
1. 调用 `Import Asset` 节点，指定源文件路径和目标包路径。
2. 选择或创建一个管道对象（`UInterchangePipeline` 子类实例）。
3. 管道执行后，从结果容器中读取导入的资产列表。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeImportModule.h"         // 主模块
#include "InterchangeManager.h"               // 导入管理器
#include "InterchangePipelineBase.h"          // 管道基类
#include "InterchangeImportLog.h"             // 日志类别
```

### 基本用法

**手动触发导入**（常用于自动化工具）：

```cpp
// Source: Engine/Plugins/Interchange/Runtime/Source/Import/Private/InterchangeManager.cpp
UInterchangeManager& Manager = UInterchangeManager::GetInterchangeManager();
FImportAssetParameters Params;
Params.bIsAutomated = true;  // 静默导入，不触发对话框

UInterchangeResult* Result = nullptr;
TArray<UObject*> ImportedObjects = Manager.ImportAsset(
    TEXT("/Game/Imported/MyMesh"),
    TEXT("D:/Assets/MyMesh.fbx"),
    Params,
    Result
);
```

**自定义管道示例**（在导入时修改材质）：

```cpp
// Source: Engine/Plugins/Interchange/Runtime/Source/Pipelines/Private/InterchangeGenericMeshPipeline.cpp
class UMyCustomPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()
public:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* NodeContainer) override
    {
        // 遍历所有材质节点，添加后缀
        NodeContainer->IterateNodesOfType<UInterchangeMaterialInstanceFactoryNode>(
            [](const FString& NodeUid, UInterchangeBaseNode* Node)
            {
                UInterchangeMaterialInstanceFactoryNode* MatNode = Cast<UInterchangeMaterialInstanceFactoryNode>(Node);
                if (MatNode)
                {
                    MatNode->SetDisplayLabel(MatNode->GetDisplayLabel() + TEXT("_Imported"));
                }
            });
    }
};
```

### 进阶用法

**MaterialX 材质转换**（内部使用）：

`InterchangeImport` 内置了 MaterialX 解析器，可将 `.mtlx` 文件中的 PBR 着色器转换为 UE 材质编辑器节点图。

```cpp
// Source: Engine/Plugins/Interchange/Runtime/Source/Import/Private/MaterialX/MaterialXManager.cpp
// 使用 MaterialX 导出器创建材质
TSharedPtr<FMaterialXBase> ShaderHandler = FMaterialXOpenPBRSurfaceShader::MakeInstance(NodeContainer);
UInterchangeBaseNode* TranslatedNode = ShaderHandler->Translate(MaterialXNode);
// TranslatedNode 会包含完整的材质表达式节点，供后续工厂生成 UMaterialInstance。
```

**动画烘焙**（用于骨骼网格体动画导入）：

```cpp
// Source: Engine/Plugins/Interchange/Runtime/Source/Import/Private/Animation/InterchangeAnimationHelper.cpp
// 将 GLTF 动画烘焙为 UE 动画序列
UE::Interchange::Gltf::Private::GetBakedAnimationTransformPayloadData(
    PayLoadKey,
    GltfAsset,
    OutPayloadData
);
```

## Demo 示例

**最小化导入示例**（在游戏模块中调用）：

```cpp
// MyImportActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InterchangeManager.h"
#include "MyImportActor.generated.h"

UCLASS()
class AMyImportActor : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Import")
    void ImportMyAsset(const FString& SourceFile, const FString& DestinationPath);
};

// MyImportActor.cpp
#include "MyImportActor.h"
#include "InterchangeManager.h"

void AMyImportActor::ImportMyAsset(const FString& SourceFile, const FString& DestinationPath)
{
    UInterchangeManager& Mgr = UInterchangeManager::GetInterchangeManager();
    FImportAssetParameters Params;
    Params.bIsAutomated = true;

    UInterchangeResult* Result = nullptr;
    TArray<UObject*> Assets = Mgr.ImportAsset(
        *DestinationPath,
        *SourceFile,
        Params,
        Result
    );

    if (Result && Result->IsSuccess())
    {
        UE_LOG(LogTemp, Log, TEXT("Imported %d assets"), Assets.Num());
    }
}
```

> 注意：需要在模块的 `Build.cs` 中添加依赖 `"InterchangeImport"`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 核心定义（节点、工厂等） |
| `InterchangeDispatcher` | 外部进程调度（用于异步解析） |
| `InterchangeFbxParser` | FBX 文件解析 |
| `GLTFCore` | GLTF/GLB 文件解析 |
| `MaterialX` | MaterialX 材质解析（可选） |
| `AudioFormat` | 音频格式解码（WAV/OGG/FLAC/MP3/OPUS） |
| `Draco` | Draco 压缩网格体解压（可选依赖） |

无特殊依赖（仅标准 Core/Engine/等）。

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` 修复了重新导入包含骨骼网格体的文件时编辑器挂起的问题
- 2025-10-23 `0158cf6a` 移除 LOD 组中非预期的 LOD 特化
- 2025-10-21 `63c630c0` 修复静态网格体导入时缺少关卡序列动画的问题
- 2025-10-17 `765b3a10` 修复非 Unity 构建中 InterchangeWorker 的编译错误
- 2025-10-17 `2c91170f` 替换参考路径，移除过时的 PhongSurfaceMaterial 引用

### 维护评价

- **创建时间**：约 2025 年 10 月（距今不到 1 年）
- **最近更新**：持续活跃，最新修复为 2025 年 12 月（约 2 个月前）
- **活跃度**：高频更新，专注 bug 修复和稳定性
- **风险**：插件标记为 Beta，导入流程复杂，某些边缘情况可能不稳定
- **推荐度**：推荐用于新项目导入需求，但需注意 API 仍在演进，生产环境建议锁定版本并充分测试。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/interchange-framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/InterchangeWorker/Tests)