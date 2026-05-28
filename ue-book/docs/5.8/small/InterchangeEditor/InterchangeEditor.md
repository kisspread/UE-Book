# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 互换编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-12-08 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

Interchange Editor 是 UE5 Interchange 导入框架的**编辑器端 UI 与管线暴露层**。它解决的核心问题是：让编辑器能够配置、执行和管理通过 Interchange 框架进行的资产导入操作。

具体来说，这个插件提供：

1. **场景导入资产（Scene Import Asset）管理**：将一次完整的场景导入操作（包括多个 Actor 和资产）封装为一个可管理的资产对象，支持整体重置
2. **导入资产重置（Reset）**：将通过 Interchange 导入的资产或 Actor 恢复到初始导入状态，或从源文件重新导入
3. **关卡实例（Level Instance）编辑支持**：对通过 Interchange 导入的关卡实例提供进入编辑模式、提交/放弃更改等操作
4. **管线设置缓存**：管理导入管线的配置缓存，确保导入设置的变更能被正确追踪
5. **FBX 导入数据转换**：在不同资产类型之间转换 FBX 导入数据
6. **上下文菜单扩展**：在关卡编辑器的右键菜单中添加 Interchange 重置选项

它不是独立的导入器，而是将 Interchange 核心框架的功能桥接到 Unreal Editor 的 UI 和工作流中。

## 使用场景

- 你通过 Interchange 导入了一个 FBX/glTF 场景文件，包含多个模型和 Actor → 用 Scene Import Asset 进行整体管理，需要重新导入时一键 Reset
- 你修改了源模型文件（如 FBX），想让已导入的资产同步更新 → 选中 Actor 或资产执行 Reset
- 你通过 Interchange 导入了一个关卡实例，需要编辑其中的子 Actor → 进入 Level Instance 编辑模式
- 你的项目有自定义导入管线，需要缓存和管理管线设置 → 由管线缓存处理器自动管理
- 你需要在蓝图中批量重置通过 Interchange 导入的多个 Actor → 使用 BlueprintCallable 节点

## 蓝图用法

`UInterchangeEditorScriptLibrary` 是一个 `UBlueprintFunctionLibrary`，提供了所有蓝图可调用的静态函数，功能分组如下：

### 资产重置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResetSceneImportAsset` | 重置场景导入资产，恢复所有关联的 Actor 和导入资产 | `UInterchangeEditorScriptLibrary` |
| `ResetLevelAsset` | 重置整个关卡资产 | `UInterchangeEditorScriptLibrary` |
| `ResetActors` | 批量重置指定的 Actor 数组 | `UInterchangeEditorScriptLibrary` |
| `CanResetActor` | 检查指定 Actor 是否可被重置 | `UInterchangeEditorScriptLibrary` |
| `CanResetWorld` | 检查指定 World 是否可被重置 | `UInterchangeEditorScriptLibrary` |

### 关卡实例节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LevelInstanceEnterEditMode` | 使关卡实例进入编辑模式，返回是否成功 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceCommit` | 提交或放弃关卡实例的修改 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetEditableActors` | 获取进入编辑模式后可编辑的 Actor 列表 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetActors` | 获取关卡实例中所有 Actor（无需进入编辑模式） | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

**批量重置通过 Interchange 导入的 Actor**：

1. 获取目标 Actor 引用数组（如通过 GetAllActorsOfClass）
2. 对每个 Actor 连接 `CanResetActor` 节点，筛选可重置的 Actor
3. 将筛选结果传入 `ResetActors` 节点执行重置

**编辑关卡实例中的内容**：

1. 获取关卡实例 Actor 引用
2. 调用 `LevelInstanceEnterEditMode` 进入编辑模式
3. 调用 `LevelInstanceGetEditableActors` 获取可编辑的 Actor 列表
4. 对 Actor 进行所需修改
5. 调用 `LevelInstanceCommit`，将 `bDiscardChanges` 设为 `false` 提交更改

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorScriptLibrary.h"
```

### 基本用法

**重置场景导入资产**：

```cpp
// 重置通过 Interchange 导入的场景资产，恢复所有关联 Actor 和资产到初始状态
UInterchangeSceneImportAsset* SceneAsset = GetSceneImportAsset(); // 获取场景导入资产
if (SceneAsset)
{
    UInterchangeEditorScriptLibrary::ResetSceneImportAsset(SceneAsset);
}
```

**检查并重置 Actor**：

```cpp
// 先检查 Actor 是否可重置，再执行重置
TArray<AActor*> ActorsToReset;
for (AActor* Actor : SelectedActors)
{
    if (UInterchangeEditorScriptLibrary::CanResetActor(Actor))
    {
        ActorsToReset.Add(Actor);
    }
}
UInterchangeEditorScriptLibrary::ResetActors(ActorsToReset);
```

### 进阶用法

**关卡实例完整编辑流程**：

```cpp
// 完整的关卡实例编辑流程：进入编辑 → 获取 Actor → 修改 → 提交
ALevelInstance* LevelInstance = GetLevelInstance();
if (LevelInstance)
{
    // 1. 进入编辑模式
    bool bSuccess = UInterchangeEditorScriptLibrary::LevelInstanceEnterEditMode(LevelInstance);
    
    if (bSuccess)
    {
        // 2. 获取可编辑的 Actor
        const TArray<AActor*>& EditableActors = 
            UInterchangeEditorScriptLibrary::LevelInstanceGetEditableActors(LevelInstance);
        
        // 3. 对 Actor 进行修改（示例：移动位置）
        for (AActor* Actor : EditableActors)
        {
            Actor->SetActorLocation(Actor->GetActorLocation() + FVector(100.f, 0.f, 0.f));
        }
        
        // 4. 提交更改（bDiscardChanges = false 表示提交）
        UInterchangeEditorScriptLibrary::LevelInstanceCommit(LevelInstance, false);
        
        // 如需放弃更改，改为：
        // UInterchangeEditorScriptLibrary::LevelInstanceCommit(LevelInstance, true);
    }
}
```

**不进入编辑模式获取关卡实例 Actor**：

```cpp
// LevelInstanceGetActors 不需要进入编辑模式即可获取所有 Actor
TArray<AActor*> AllActors = UInterchangeEditorScriptLibrary::LevelInstanceGetActors(LevelInstance);
UE_LOG(LogInterchangeEditor, Log, TEXT("Level instance contains %d actors"), AllActors.Num());
```

**使用模块可用性检查**：

```cpp
#include "InterchangeEditorModule.h"

// 在依赖 Interchange Editor 功能前检查模块是否可用
if (FInterchangeEditorModule::IsAvailable())
{
    FInterchangeEditorModule& Module = FInterchangeEditorModule::Get();
    // 使用模块功能...
}
```

## Demo 示例

**InterchangeEditorScriptLibrary** — 完整的资产重置与关卡实例编辑示例：

```cpp
// MyInterchangeHelper.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyInterchangeHelper.generated.h"

class AActor;
class ALevelInstance;
class UInterchangeSceneImportAsset;

UCLASS(BlueprintType, Blueprintable)
class YOURPROJECT_API UMyInterchangeHelper : public UObject
{
    GENERATED_BODY()

public:
    /**
     * 安全重置场景导入资产，带日志输出
     */
    UFUNCTION(BlueprintCallable, Category="Interchange Helper")
    static bool SafeResetSceneImportAsset(UInterchangeSceneImportAsset* SceneAsset);

    /**
     * 获取关卡实例中的所有 Actor 信息
     */
    UFUNCTION(BlueprintCallable, Category="Interchange Helper")
    static TArray<FString> GetLevelInstanceActorNames(ALevelInstance* LevelInstance);

    /**
     * 完整的关卡实例编辑流程
     */
    UFUNCTION(BlueprintCallable, Category="Interchange Helper")
    static bool EditLevelInstance(ALevelInstance* LevelInstance);
};
```

```cpp
// MyInterchangeHelper.cpp
#include "MyInterchangeHelper.h"
#include "InterchangeEditorScriptLibrary.h"
#include "LevelInstance/LevelInstanceActor.h"

bool UMyInterchangeHelper::SafeResetSceneImportAsset(UInterchangeSceneImportAsset* SceneAsset)
{
    if (!SceneAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("SafeResetSceneImportAsset: SceneAsset is null"));
        return false;
    }

    UInterchangeEditorScriptLibrary::ResetSceneImportAsset(SceneAsset);
    UE_LOG(LogTemp, Log, TEXT("Successfully reset scene import asset: %s"), *SceneAsset->GetName());
    return true;
}

TArray<FString> UMyInterchangeHelper::GetLevelInstanceActorNames(ALevelInstance* LevelInstance)
{
    TArray<FString> Result;
    if (!LevelInstance)
    {
        return Result;
    }

    TArray<AActor*> Actors = UInterchangeEditorScriptLibrary::LevelInstanceGetActors(LevelInstance);
    Result.Reserve(Actors.Num());
    for (AActor* Actor : Actors)
    {
        if (Actor)
        {
            Result.Add(Actor->GetName());
        }
    }
    return Result;
}

bool UMyInterchangeHelper::EditLevelInstance(ALevelInstance* LevelInstance)
{
    if (!LevelInstance)
    {
        return false;
    }

    // 进入编辑模式
    if (!UInterchangeEditorScriptLibrary::LevelInstanceEnterEditMode(LevelInstance))
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to enter edit mode for level instance"));
        return false;
    }

    // 获取并操作 Actor
    const TArray<AActor*>& EditableActors = 
        UInterchangeEditorScriptLibrary::LevelInstanceGetEditableActors(LevelInstance);
    UE_LOG(LogTemp, Log, TEXT("Found %d editable actors"), EditableActors.Num());

    // 提交更改
    UInterchangeEditorScriptLibrary::LevelInstanceCommit(LevelInstance, false);
    return true;
}
```

## 模块依赖

该插件由三个模块组成，以下是各模块的独特依赖（标准 Core/Engine 等已省略）：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 导入框架核心 |
| `InterchangeFramework` | Interchange 框架实现 |
| `InterchangeNodes` | Interchange 节点定义 |
| `LevelInstance` | 关卡实例功能支持 |
| `Engine` | 关卡/Actor 基础（标准依赖） |
| `InterchangeImport` | Interchange 导入器实现 |
| `InterchangePipelines` | 导入管线基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 新增临时挂起自动保存器的功能 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除动画帧对齐和 glTF 转换器帧对齐器 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loadi | 新增无需加载即可获取关卡实例 Actor 的接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构静态网格和骨骼网格的导入设置 |

### 维护评价

- **活跃维护**：最近 1 个月内有多次实质性更新（2026 年 4-5 月）
- **功能演进中**：导入管线和设置持续重构，表明 Interchange 框架仍在快速迭代
- **API 扩展**：`cc360b1e` 新增了 `LevelInstanceGetActors` 接口，说明编辑器脚本 API 在持续扩展
- **Epic 官方维护**：由 Epic Games 直接维护，作为 UE5 推荐的资产导入框架

**推荐使用**：Interchange 是 UE5 官方推荐的下一代资产导入框架（替代旧的 FBX Importer），该编辑器插件是使用 Interchange 工作流的必备组件。随着 UE5 对旧导入器的逐步废弃，建议新项目采用 Interchange。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- 官方文档：暂无
- 测试用例：未在插件目录内发现独立测试文件