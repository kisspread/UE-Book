# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable) | |

---

## 用途

Mutable 是 UE5 的**运行时可定制对象系统**，解决游戏中角色/物品外观组合爆炸的核心问题。

**传统痛点**：假设一个角色有 10 种发型 × 5 种肤色 × 8 套服装 × 6 种配饰 = 2400 种组合。预创建所有组合会导致资产数量指数级增长、内存爆炸、美术工作量不可控。

**Mutable 的解决方案**：通过声明式节点图定义"定制空间"，在运行时根据玩家选择的参数**动态生成**最终的骨骼网格体、材质和纹理。只需存储基础部件和组合规则，无需预创建所有组合。

### 架构层次

```
┌─────────────────────────────────────────────────┐
│  CustomizableObjectEditor  (编辑器：节点图、预览、烘焙)  │
├─────────────────────────────────────────────────┤
│  MutableTools              (编译：图 → 运行时数据)      │
├─────────────────────────────────────────────────┤
│  CustomizableObject        (UE 集成：资产、实例、系统)   │
├─────────────────────────────────────────────────┤
│  MutableRuntime            (运行时：网格体/材质/纹理生成) │
├─────────────────────────────────────────────────┤
│  MutableValidation         (验证与测试)                │
└─────────────────────────────────────────────────┘
```

### 核心概念

| 概念 | 说明 |
|---|---|
| **CustomizableObject** | 可定制对象的定义/模板（类似类），包含节点图 |
| **CustomizableObjectInstance** | 一个具体配置（类似实例），持有参数值 |
| **参数类型** | Bool、Int、Float、Color、Enum、String、Projector（投影器）、Transform |
| **状态 (State)** | 不同上下文的配置（如游戏中 vs 菜单），可控制 LOD 和细节级别 |
| **扩展数据 (ExtensionData)** | 自定义数据类型，可将任意 UE 资产导入节点图 |
| **投影器 (Projector)** | 用于贴花、纹身、Logo 等投射到表面的参数类型 |

---

## 使用场景

- 你在做 RPG / MMO，需要角色外观定制（发型、肤色、服装、装备混搭） → **用 Mutable**
- 你有大量视觉变体的物品（武器皮肤、载具涂装、家具款式） → **用 Mutable**
- 你需要运行时动态合并多个骨骼网格体 / 材质 → **用 Mutable**
- 你想减少内存占用，避免预烘焙所有组合 → **用 Mutable**
- 你需要为 NPC 生成随机外观群体 → **用 Mutable 的 Population 系统**
- 你有 DLC / 版本化内容，需要控制哪些子对象包含在当前版本 → **用 Mutable 的 VersionBridge**

---

## 蓝图用法

Mutable 的编辑器模块提供了蓝图函数库，用于自动化创建和编译可定制对象。运行时蓝图 API 位于 `CustomizableObject` 模块中（`UCustomizableObjectInstance` 的参数设置/更新接口）。

### 核心节点（编辑器）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NewCustomizableObject` | 在指定包路径创建新的可定制对象资产 | `UCustomizableObjectEditorFunctionLibrary` |
| `CompileCustomizableObjectSynchronously` | 同步编译可定制对象（⚠️ 已废弃，改用 `UCustomizableObject::Compile`） | `UCustomizableObjectEditorFunctionLibrary` |

### 使用示例（蓝图描述）

**创建新的可定制对象**：
1. 添加 `NewCustomizableObject` 节点
2. 构造 `FNewCustomizableObjectParameters` 结构体：
   - `PackagePath` → `"/Game/MyCharacters"`
   - `AssetName` → `"Warrior"`
   - `ParentObject` → 可选，连接父 CO 实现继承
   - `ParentGroupNode` → 可选，指定父对象的分组节点
3. 输出引脚即为新创建的 `UCustomizableObject` 引用

---

## C++ 用法

### 头文件引入

```cpp
// 编辑器功能（创建、编译、烘焙）
#include "MuCOE/CustomizableObjectEditorFunctionLibrary.h"
#include "MuCOE/CompileRequest.h"
#include "MuCOE/ExtensionDataCompilerInterface.h"
#include "MuCOE/CustomizableObjectInstanceBakingUtils.h"
#include "MuCOE/CustomizableObjectBenchmarkingUtils.h"

// 运行时功能（实例、参数）
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
```

### 基本用法：创建和编译可定制对象

```cpp
// 来源: CustomizableObjectEditorFunctionLibrary.h

// 创建新的可定制对象
FNewCustomizableObjectParameters Params;
Params.PackagePath = TEXT("/Game/MyCustomizableObjects");
Params.AssetName = TEXT("MyCharacter");
Params.ParentObject = nullptr;  // 无父对象（根 CO）
Params.ParentGroupNode = TEXT("");

UCustomizableObject* NewCO = UCustomizableObjectEditorFunctionLibrary::NewCustomizableObject(Params);

// 编译（推荐方式）
if (NewCO)
{
    NewCO->Compile();
}
```

### 进阶用法：异步编译与烘焙

```cpp
// 来源: CustomizableObjectInstanceBakingUtils.h

UCustomizableObjectInstance* Instance = GetMyInstance();

// 1. 调度异步编译（可选择只编译实例所需数据）
FCompileNativeDelegate CompileDelegate;
CompileDelegate.BindLambda([](ECompilationResultPrivate Result)
{
    UE_LOG(LogMutable, Log, TEXT("Compilation result: %d"), (int32)Result);
});
ScheduleCOCompilationForBaking(*Instance, CompileDelegate, /*bPerformPartialCompilation=*/ false);

// 2. 调度实例更新
FInstanceUpdateNativeDelegate UpdateDelegate;
UpdateDelegate.BindLambda([]()
{
    UE_LOG(LogMutable, Log, TEXT("Instance updated, ready to bake"));
});
ScheduleInstanceUpdateForBaking(*Instance, UpdateDelegate);

// 3. 烘焙实例资源到磁盘
FBakingConfiguration BakingConfig;
TMap<UPackage*, EPackageSaveResolutionType> SavedPackages;
bool bSuccess = BakeCustomizableObjectInstance(
    *Instance, BakingConfig, /*bIsUnattendedExecution=*/ true, SavedPackages);
```

### 进阶用法：自定义扩展数据节点

```cpp
// 来源: ICustomizableObjectExtensionNode.h, ExtensionDataCompilerInterface.h

// 实现自定义扩展数据节点，将任意 UE 资产导入 CO 图
UCLASS()
class UMyExtensionDataNode : public UCustomizableObjectNode,
                             public ICustomizableObjectExtensionNode
{
    GENERATED_BODY()

public:
    virtual UE::Mutable::Private::Ptr<UE::Mutable::Private::NodeExtensionData>
    GenerateMutableNode(FExtensionDataCompilerInterface& CompilerInterface) const override
    {
        FInstancedStruct MyData;
        // ... 填充自定义数据 ...

        // 方式 A：流式加载（按需加载，独立包）
        auto StreamedData = CompilerInterface.MakeStreamedExtensionData(MoveTemp(MyData));

        // 方式 B：始终加载（嵌入 CO，随 CO 一起加载）
        // auto AlwaysLoadedData = CompilerInterface.MakeAlwaysLoadedExtensionData(MoveTemp(MyData));

        // 注册生成的节点
        CompilerInterface.AddGeneratedNode(this);

        return StreamedData;
    }
};
```

### 进阶用法：版本桥接（DLC / 版本化内容）

```cpp
// 来源: CustomizableObjectVersionBridge.h

UCLASS()
class UMyVersionBridge : public UObject, public ICustomizableObjectVersionBridgeInterface
{
    GENERATED_BODY()

public:
    // 判断子 CO 的版本是否包含在当前发布中
    virtual bool IsVersionStructIncludedInCurrentRelease(
        const FInstancedStruct& VersionStruct) const override
    {
        if (const auto* MyVersion = VersionStruct.GetPtr<FMyGameVersion>())
        {
            return MyVersion->ReleaseVersion <= GetCurrentReleaseVersion();
        }
        return false;
    }

    // 用于派生数据缓存键的版本字符串
    virtual FString GetCurrentVersionAsString() const override
    {
        return FString::Printf(TEXT("%d"), GetCurrentReleaseVersion());
    }
};
```

### 进阶用法：基准测试

```cpp
// 来源: CustomizableObjectBenchmarkingUtils.h

UCustomizableObject* CO = GetMyCustomizableObject();
TSpscQueue<TStrongObjectPtr<UCustomizableObjectInstance>> GeneratedInstances;
uint32 SuccessCount = 0;

// 为每个状态生成确定性实例集（相同 CO → 相同结果）
bool bOK = CustomizableObjectBenchmarkingUtils::GenerateDeterministicSetOfInstances(
    *CO,
    /*InstancesPerState=*/ 4,    // 每个状态 4 个实例
    GeneratedInstances,
    SuccessCount
);

int32 OptLevel = CustomizableObjectBenchmarkingUtils::GetOptimizationLevelForBenchmarking();
```

---

## Demo 示例

以下是一个完整的编辑器自动化示例，展示如何通过 C++ 创建、编译和烘焙