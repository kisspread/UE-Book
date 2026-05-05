# Editor Scripting Utilities

> Helper functions to script your own UE editor functionalities with Blueprint or other scripting tools.

| 属性 | 值 |
|---|---|
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorScriptingUtilities` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorScriptingUtilities) | |

## ⚠️ 重要警告：此插件已废弃

从 UE 5.0 开始，此插件中的 **大量函数已被标记为废弃（Deprecated）**。Epic 将功能迁移至独立的 Editor Subsystem 中：

| 原类 | 替代方案 |
|---|---|
| `UEditorLevelLibrary`（大部分函数） | `UActorUtilitiesSubsystem`、`ULevelEditorSubsystem`、`UUnrealEditorSubsystem` |
| `UDEPRECATED_EditorStaticMeshLibrary` | `UStaticMeshEditorSubsystem`（Static Mesh Editor Subsystem 插件） |
| `UDEPRECATED_EditorSkeletalMeshLibrary` | `USkeletalMeshEditorSubsystem`（Skeletal Mesh Editor Subsystem 插件） |

仍**未废弃**的类：
- `UEditorAssetLibrary` — 资产管理操作（加载、保存、删除、重命名等）
- `UEditorDialogLibrary` — 编辑器弹窗对话框
- `UEditorFilterLibrary` — Actor/对象过滤工具

> 此外，`.uplugin` 中 `EnabledByDefault=false` 且 `IsBetaVersion=true`，说明此插件一直处于实验状态。新项目应优先使用替代方案。

## 用途

Editor Scripting Utilities 是 UE 编辑器脚本化的"瑞士军刀"。它暴露了大量编辑器操作为 Blueprint 可调用的静态函数，使你无需编写 C++ 模块即可在蓝图中实现资产批处理、关卡管理、网格体操作、弹窗交互和对象筛选等功能。

这个插件存在是因为 UE 编辑器的很多操作（如批量保存资产、合并网格体、管理 LOD）原本只能通过 UI 菜单完成。此插件将它们封装为脚本化 API，让自动化编辑器任务成为可能。

## 使用场景

- 你需要批量重命名/移动/删除 Content Browser 中的资产 → 用 `UEditorAssetLibrary`
- 你需要在蓝图编辑器工具中创建/销毁 Actor → 用 `UEditorLevelLibrary`（但注意大部分已废弃）
- 你需要给 Static Mesh 添加/移除碰撞体 → 用 `UDEPRECATED_EditorStaticMeshLibrary`（替代方案：`UStaticMeshEditorSubsystem`）
- 你需要弹出一个 Yes/No 对话框让用户确认操作 → 用 `UEditorDialogLibrary`
- 你需要按名称/类型/标签筛选 Actor 列表 → 用 `UEditorFilterLibrary`
- 你需要查看/编辑资产的 metadata 标签 → 用 `UEditorAssetLibrary::GetMetadataTag` / `SetMetadataTag`

## 蓝图用法

### UEditorAssetLibrary — 资产管理

#### 资产加载与查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadAsset` | 按路径加载资产（已加载则复用） | `UEditorAssetLibrary` |
| `LoadBlueprintClass` | 加载蓝图资产并返回其生成的类 | `UEditorAssetLibrary` |
| `DoesAssetExist` | 检查资产是否存在于 Content Browser | `UEditorAssetLibrary` |
| `DoAssetsExist` | 批量检查多个资产是否存在 | `UEditorAssetLibrary` |
| `FindAssetData` | 获取资产的 `FAssetData`（用于 AssetRegistryHelpers） | `UEditorAssetLibrary` |
| `GetPathNameForLoadedAsset` | 获取已加载资产的路径名 | `UEditorAssetLibrary` |
| `FindPackageReferencersForAsset` | 查找引用指定资产的其他资产 | `UEditorAssetLibrary` |

#### 资产 CRUD 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DuplicateAsset` / `DuplicateLoadedAsset` | 复制资产 | `UEditorAssetLibrary` |
| `DuplicateDirectory` | 复制整个目录 | `UEditorAssetLibrary` |
| `RenameAsset` / `RenameLoadedAsset` | 重命名（移动）资产 | `UEditorAssetLibrary` |
| `RenameDirectory` | 重命名目录 | `UEditorAssetLibrary` |
| `DeleteAsset` / `DeleteLoadedAsset` | 删除资产（强制删除，不检查引用） | `UEditorAssetLibrary` |
| `DeleteLoadedAssets` | 批量删除已加载资产 | `UEditorAssetLibrary` |
| `DeleteDirectory` | 递归删除目录及其所有资产 | `UEditorAssetLibrary` |
| `ConsolidateAssets` | 合并资产（将所有引用重定向到目标资产，然后删除源资产） | `UEditorAssetLibrary` |

#### 资产保存与版本控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SaveAsset` / `SaveLoadedAsset` | 保存资产包 | `UEditorAssetLibrary` |
| `SaveLoadedAssets` | 批量保存已加载资产 | `UEditorAssetLibrary` |
| `SaveDirectory` | 保存目录中的所有资产 | `UEditorAssetLibrary` |
| `CheckoutAsset` / `CheckoutLoadedAsset` | 从版本控制签出资产 | `UEditorAssetLibrary` |
| `CheckoutLoadedAssets` | 批量签出 | `UEditorAssetLibrary` |
| `CheckoutDirectory` | 签出整个目录 | `UEditorAssetLibrary` |

#### 目录操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesDirectoryExist` | 检查目录是否存在 | `UEditorAssetLibrary` |
| `DoesDirectoryHaveAssets` | 检查目录是否包含资产 | `UEditorAssetLibrary` |
| `MakeDirectory` | 创建目录 | `UEditorAssetLibrary` |
| `ListAssets` | 列出目录中的所有资产 | `UEditorAssetLibrary` |
| `ListAssetByTagValue` | 按 Tag/Value 查找资产 | `UEditorAssetLibrary` |
| `GetTagValues` | 获取资产的 AssetRegistry Tag 值 | `UEditorAssetLibrary` |

#### Metadata 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetadataTagValues` | 获取已加载资产的所有 metadata 标签 | `UEditorAssetLibrary` |
| `GetMetadataTag` | 获取指定标签的值 | `UEditorAssetLibrary` |
| `SetMetadataTag` | 设置 metadata 标签 | `UEditorAssetLibrary` |
| `RemoveMetadataTag` | 删除 metadata 标签 | `UEditorAssetLibrary` |

#### Content Browser 同步

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SyncBrowserToObjects` | 在 Content Browser 中定位并选中指定资产（异步操作） | `UEditorAssetLibrary` |
| `GetProjectRootAssetDirectory` | 获取项目根资产目录（UEFN 用） | `UEditorAssetLibrary` |

---

### UEditorLevelLibrary — 关卡/世界管理（大部分已废弃）

> ⚠️ 此类中几乎所有函数已在 UE 5.0 标记为废弃。下表标注了每个函数的替代方案。

| 节点 | 说明 | 替代方案 |
|---|---|---|
| `GetAllLevelActors` | 获取世界中所有已加载的 Actor | `UActorUtilitiesSubsystem` |
| `GetAllLevelActorsComponents` | 获取所有 Actor 的组件 | `UActorUtilitiesSubsystem` |
| `GetSelectedLevelActors` | 获取当前选中的 Actor | `UActorUtilitiesSubsystem` |
| `SetSelectedLevelActors` | 设置选中的 Actor | `UActorUtilitiesSubsystem` |
| `SpawnActorFromObject` | 从对象/资产在编辑器世界中生成 Actor | `UActorUtilitiesSubsystem` |
| `SpawnActorFromClass` | 从类/蓝图生成 Actor | `UActorUtilitiesSubsystem` |
| `DestroyActor` | 销毁 Actor | `UActorUtilitiesSubsystem` |
| `GetEditorWorld` | 获取编辑器世界 | `UUnrealEditorSubsystem` |
| `GetGameWorld` | 获取游戏世界 | `UUnrealEditorSubsystem` |
| `NewLevel` | 创建新关卡 | `ULevelEditorSubsystem` |
| `NewLevelFromTemplate` | 从模板创建新关卡 | `ULevelEditorSubsystem` |
| `LoadLevel` | 加载关卡 | `ULevelEditorSubsystem` |
| `SaveCurrentLevel` | 保存当前关卡 | `ULevelEditorSubsystem` |
| `SaveAllDirtyLevels` | 保存所有脏关卡 | `ULevelEditorSubsystem` |
| `PilotLevelActor` | 以 Actor 视角导航 | `ULevelEditorSubsystem` |
| `EjectPilotLevelActor` | 退出 Actor 视角 | `ULevelEditorSubsystem` |
| `EditorPlaySimulate` | 启动 PIE | `ULevelEditorSubsystem` |
| `GetLevelViewportCameraInfo` | 获取视口相机信息 | `UUnrealEditorSubsystem` |
| `SetLevelViewportCameraInfo` | 设置视口相机信息 | `UUnrealEditorSubsystem` |
| `ConvertActors` | 转换 Actor 类型 | `UActorUtilitiesSubsystem` |
| `ReplaceMeshComponentsMaterials` | 替换网格体材质 | `UStaticMeshEditorSubsystem` |
| `ReplaceMeshComponentsMeshes` | 替换网格体 | `UStaticMeshEditorSubsystem` |
| `JoinStaticMeshActors` | 合并多个 Static Mesh Actor | `UStaticMeshEditorSubsystem` |
| `MergeStaticMeshActors` | 合并网格体为唯一网格 | `UStaticMeshEditorSubsystem` |
| `CreateProxyMeshActor` | 创建代理网格 Actor | `UStaticMeshEditorSubsystem` |

少数未废弃的函数：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EditorEndPlay` | 结束 PIE | `UEditorLevelLibrary` |
| `GetPIEWorlds` | 获取 PIE 世界列表 | `UEditorLevelLibrary` |
| `ReplaceSelectedActors` | 替换选中的 Actor | `UEditorLevelLibrary` |

---

### UDEPRECATED_EditorStaticMeshLibrary — Static Mesh 操作（全部已废弃）

> 替代方案：`UStaticMeshEditorSubsystem`（Static Mesh Editor Subsystem 插件）

#### LOD 管理

| 节点 | 说明 |
|---|---|
| `SetLods` / `SetLodsWithNotification` | 重新生成 LOD（指定减面参数） |
| `GetLodReductionSettings` / `SetLodReductionSettings` | 获取/设置 LOD 减面参数 |
| `GetLodBuildSettings` / `SetLodBuildSettings` | 获取/设置 LOD 构建参数 |
| `GetLodCount` | 获取 LOD 数量 |
| `GetLodScreenSizes` | 获取各 LOD 的屏幕尺寸阈值 |
| `RemoveLods` | 移除所有 LOD（保留 LOD 0） |
| `ImportLOD` | 从 FBX 导入/重新导入 LOD |
| `ReimportAllCustomLODs` | 重新导入所有自定义 LOD |
| `SetLodFromStaticMesh` | 从另一个 Static Mesh 复制 LOD |

#### 碰撞管理

| 节点 | 说明 |
|---|---|
| `AddSimpleCollisions` | 添加简单碰撞体（Box/Sphere/Capsule 等） |
| `SetConvexDecompositionCollisions` | 设置凸分解碰撞 |
| `BulkSetConvexDecompositionCollisions` | 批量设置凸分解碰撞 |
| `RemoveCollisions` | 移除所有碰撞 |
| `GetSimpleCollisionCount` | 获取简单碰撞数量 |
| `GetConvexCollisionCount` | 获取凸碰撞数量 |
| `GetCollisionComplexity` | 获取碰撞追踪行为 |
| `EnableSectionCollision` | 启用/禁用特定 LOD Section 的碰撞 |
| `IsSectionCollisionEnabled` | 检查 Section 碰撞是否启用 |

#### UV 通道管理

| 节点 | 说明 |
|---|---|
| `GetNumUVChannels` | 获取 UV 通道数量 |
| `AddUVChannel` | 添加空 UV 通道 |
| `InsertUVChannel` | 在指定位置插入 UV 通道 |
| `RemoveUVChannel` | 移除 UV 通道 |
| `GeneratePlanarUVChannel` | 生成平面 UV 映射 |
| `GenerateCylindricalUVChannel` | 生成柱面 UV 映射 |
| `GenerateBoxUVChannel` | 生成盒体 UV 映射 |

#### 其他

| 节点 | 说明 |
|---|---|
| `HasVertexColors` | 检查是否有顶点色 |
| `HasInstanceVertexColors` | 检查组件实例是否有顶点色 |
| `SetGenerateLightmapUVs` | 设置是否生成光照贴图 UV |
| `GetNumberVerts` | 获取 LOD 的顶点数 |
| `GetNumberMaterials` | 获取材质数量 |
| `SetAllowCPUAccess` | 设置 CPU 访问标志 |
| `EnableSectionCastShadow` | 设置 Section 阴影投射 |

---

### UDEPRECATED_EditorSkeletalMeshLibrary — Skeletal Mesh 操作（全部已废弃）

> 替代方案：`USkeletalMeshEditorSubsystem`（Skeletal Mesh Editor Subsystem 插件）

| 节点 | 说明 |
|---|---|
| `RegenerateLOD` | 重新生成骨骼网格 LOD |
| `GetNumVerts` | 获取 LOD 顶点数 |
| `GetLODCount` | 获取 LOD 数量 |
| `ImportLOD` | 从 FBX 导入 LOD |
| `ReimportAllCustomLODs` | 重新导入所有自定义 LOD |
| `GetLodBuildSettings` / `SetLodBuildSettings` | 获取/设置 LOD 构建参数 |
| `RemoveLODs` | 移除指定 LOD |
| `RenameSocket` | 重命名骨骼 Socket |
| `StripLODGeometry` | 根据纹理遮罩裁剪 LOD 三角形 |
| `CreatePhysicsAsset` | 为骨骼网格创建物理资产 |

---

### UEditorDialogLibrary — 编辑器对话框（未废弃）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowMessage` | 显示模态消息对话框（支持 Yes/No/OK/Cancel 等按钮） | `UEditorDialogLibrary` |
| `ShowSuppressableWarningDialog` | 显示可抑制的警告对话框（用户可勾选"不再显示"） | `UEditorDialogLibrary` |
| `ShowObjectDetailsView` | 显示包含 UObject 属性编辑器的对话框 | `UEditorDialogLibrary` |
| `ShowObjectsDetailsView` | 显示包含多个 UObject 属性编辑器的对话框 | `UEditorDialogLibrary` |

### UEditorFilterLibrary — Actor/对象过滤（未废弃）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ByClass` | 按对象类过滤 | `UEditorFilterLibrary` |
| `ByIDName` | 按对象 ID 名称过滤 | `UEditorFilterLibrary` |
| `ByActorLabel` | 按 Actor 标签过滤 | `UEditorFilterLibrary` |
| `ByActorTag` | 按 Actor Tag 过滤 | `UEditorFilterLibrary` |
| `ByLayer` | 按 Layer 过滤 | `UEditorFilterLibrary` |
| `ByLevelName` | 按关卡名过滤 | `UEditorFilterLibrary` |
| `BySelection` | 按选中状态过滤 | `UEditorFilterLibrary` |

过滤器支持 `Include` / `Exclude` 模式，字符串匹配支持 `Contains` / `MatchesWildcard` / `ExactMatch` 三种方式。

---

### 使用示例（蓝图描述）

#### 批量保存所有脏资产

1. 使用 `ListAssets` 获取 `/Game/` 目录下所有资产路径（Recursive=true）
2. 使用 `SaveDirectory` 一键保存（bOnlyIfIsDirty=true, bRecursive=true）

#### 按名称筛选 Actor 后删除

1. 使用 `GetAllLevelActors` 获取所有 Actor（注意：此函数已废弃）
2. 使用 `ByActorLabel` 筛选名称包含 "Temp_" 的 Actor
3. 对结果数组循环调用 `DestroyActor`

#### 复制并重命名资产

1. 使用 `DuplicateAsset`（SourcePath=`/Game/OldName`, DestPath=`/Game/NewName`）
2. 调用 `SaveAsset` 保存复制结果

#### 弹出确认对话框后执行操作

1. 使用 `ShowMessage`（Title="确认删除", Message="是否删除选中的资产？", MessageType=YesNo）
2. 根据返回值分支：Yes → 执行删除操作

## C++ 用法

> **注意**：此插件中大部分函数为 `static` 的 BlueprintCallable，且标记为 `MinimalAPI`。C++ 中直接使用这些静态函数即可，但更推荐使用替代 Subsystem API。

### 头文件引入

```cpp
#include "EditorAssetLibrary.h"
#include "EditorDialogLibrary.h"
#include "EditorFilterLibrary.h"
// 以下头文件中的类已废弃，仅供参考
#include "EditorLevelLibrary.h"
#include "EditorStaticMeshLibrary.h"
#include "EditorSkeletalMeshLibrary.h"
```

### 基本用法：资产管理

```cpp
// 检查资产是否存在
bool bExists = UEditorAssetLibrary::DoesAssetExist(TEXT("/Game/MyFolder/MyAsset"));

// 加载资产
UObject* Asset = UEditorAssetLibrary::LoadAsset(TEXT("/Game/MyFolder/MyAsset"));

// 复制资产
UObject* Duplicated = UEditorAssetLibrary::DuplicateAsset(
    TEXT("/Game/Source/Asset"),
    TEXT("/Game/Dest/AssetCopy")
);

// 保存资产
UEditorAssetLibrary::SaveAsset(TEXT("/Game/Dest/AssetCopy"), true);

// 列出目录中的资产
TArray<FString> AssetPaths = UEditorAssetLibrary::ListAssets(
    TEXT("/Game/MyFolder/"), true, false
);
```

### 基本用法：对话框

```cpp
// 显示 Yes/No 对话框
EAppReturnType::Type Result = UEditorDialogLibrary::ShowMessage(
    FText::FromString(TEXT("确认")),
    FText::FromString(TEXT("是否继续？")),
    EAppMsgType::YesNo,
    EAppReturnType::No,
    EAppMsgCategory::Warning
);

if (Result == EAppReturnType::Yes)
{
    // 用户确认
}
```

### 基本用法：对象过滤

```cpp
// 假设已有 ActorArray
TArray<AActor*> AllActors = UEditorLevelLibrary::GetAllLevelActors(); // 已废弃

// 按类过滤
TArray<UObject*> FilteredByClass = UEditorFilterLibrary::ByClass(
    AllActors, AStaticMeshActor::StaticClass(), EEditorScriptingFilterType::Include
);

// 按名称过滤
TArray<AActor*> FilteredByName = UEditorFilterLibrary::ByActorLabel(
    AllActors,
    TEXT("Building"),
    EEditorScriptingStringMatchType::Contains,
    EEditorScriptingFilterType::Include,
    true
);

// 按 Tag 过滤
TArray<AActor*> FilteredByTag = UEditorFilterLibrary::ByActorTag(
    AllActors,
    FName(TEXT("Important")),
    EEditorScriptingFilterType::Include
);
```

### 进阶用法：Metadata 标签批量处理

```cpp
// 为所有资产添加自定义 metadata 标签
TArray<FString> Assets = UEditorAssetLibrary::ListAssets(TEXT("/Game/Characters/"), true, false);

for (const FString& AssetPath : Assets)
{
    UObject* Asset = UEditorAssetLibrary::LoadAsset(AssetPath);
    if (Asset)
    {
        // 设置标签
        UEditorAssetLibrary::SetMetadataTag(Asset, FName(TEXT("BatchID")), TEXT("2024_001"));
        UEditorAssetLibrary::SaveAsset(AssetPath);
    }
}

// 后续可按标签查找
TArray<FString> Found = UEditorAssetLibrary::ListAssetByTagValue(FName(TEXT("BatchID")), TEXT("2024_001"));
```

## Demo 示例

### 最小完整示例：编辑器工具蓝图函数库

以下 C++ 类展示如何结合 EditorScriptingUtilities 实现一个简单的编辑器工具：

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "EditorScriptingUtilities"
});
```

**MyEditorTools.h**：
```cpp
#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyEditorTools.generated.h"

UCLASS()
class UMyEditorTools : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // 批量重命名资产：将 OldPrefix 替换为 NewPrefix
    UFUNCTION(BlueprintCallable, Category = "My Tools")
    static int32 BatchRenameAssets(const FString& DirectoryPath,
                                    const FString& OldPrefix,
                                    const FString& NewPrefix);
};
```

**MyEditorTools.cpp**：
```cpp
#include "MyEditorTools.h"
#include "EditorAssetLibrary.h"

int32 UMyEditorTools::BatchRenameAssets(const FString& DirectoryPath,
                                         const FString& OldPrefix,
                                         const FString& NewPrefix)
{
    TArray<FString> Assets = UEditorAssetLibrary::ListAssets(DirectoryPath, true, false);
    int32 RenamedCount = 0;

    for (const FString& AssetPath : Assets)
    {
        // 从路径提取资产名
        FString AssetName = FPaths::GetBaseFilename(AssetPath);
        if (AssetName.StartsWith(OldPrefix))
        {
            FString NewName = AssetName.Replace(*OldPrefix, *NewPrefix);
            FString NewPath = FPaths::GetPath(AssetPath) / NewName;

            if (UEditorAssetLibrary::RenameAsset(AssetPath, NewPath))
            {
                UEditorAssetLibrary::SaveAsset(NewPath);
                ++RenamedCount;
            }
        }
    }

    return RenamedCount;
}
```

## 模块依赖

从 `EditorScriptingUtilities.Build.cs` 提取。如果你的模块需要依赖此插件，需要在 Build.cs 中添加：

| 模块 | 用途 |
|---|---|
| `EditorScriptingUtilities` | 本插件模块 |

插件自身的内部依赖（不需要使用者直接引用）：

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册表查询 |
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `StaticMeshEditor` | Static Mesh 编辑器 |
| `UnrealEd` | 编辑器框架（Private） |
| `MeshDescription` | 网格描述（Private） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具（Private） |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-05-30 | `8396b185774c` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n | 纯编译兼容性修复，将 DLL 导出宏从类型移到方法/静态变量上，无功能变更 |
| 2025-03-03 | `8d05b3a4d068` | Cleaned up LODs -> lo_ds in Python exposed API | Python 脚本 API 命名规范调整（LODs → lo_ds），无功能变更 |
| 2024-10-22 | `98a8e0e0df23` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理废弃的 include 宏，无功能变更 |

### 维护评价

- **创建时间**：2018 年 5 月（约 8 年前）
- **最近更新频率**：仅有编译/命名层面的维护性提交，**无功能性更新**
- **废弃状态**：自 UE 5.0（2022 年）起，核心功能已全面废弃并迁移至 Editor Subsystem
- **仍在维护**：是，但仅限编译兼容性修复
- **是否推荐使用**：
  - **`UEditorAssetLibrary`**：✅ 推荐使用，功能完整且未废弃
  - **`UEditorDialogLibrary`**：✅ 推荐使用，对话框功能实用
  - **`UEditorFilterLibrary`**：✅ 推荐使用，过滤工具实用
  - **`UEditorLevelLibrary`**：❌ 不推荐，已废弃，使用 `UActorUtilitiesSubsystem` / `ULevelEditorSubsystem`
  - **`EditorStaticMeshLibrary`**：❌ 不推荐，已废弃，使用 `UStaticMeshEditorSubsystem`
  - **`EditorSkeletalMeshLibrary`**：❌ 不推荐，已废弃，使用 `USkeletalMeshEditorSubsystem`

> ⚠️ 自 UE 5.0 至今（约 4 年），此插件的 Level/StaticMesh/SkeletalMesh 相关功能已无实质性更新，处于维护收尾状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorScriptingUtilities)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 替代方案源码：
  - [Static Mesh Editor Subsystem](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StaticMeshEditorSubsystem)
  - [Skeletal Mesh Editor Subsystem](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/SkeletalMeshEditorSubsystem)
