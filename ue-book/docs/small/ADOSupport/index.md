# ADO Support

> ADO (ActiveX Data Objects) Database Support

| 属性 | 值 |
|---|---|
| 分类 | Database |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | ADOSupport (Runtime) |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/ADOSupport) | |

## 用途

ADOSupport 是 UE5 数据库连接系统的 ADO 后端实现。它通过 Windows COM 技术的 ActiveX Data Objects（ADO）接口，让 Unreal Engine 能够连接和查询 SQL Server 等关系型数据库。

这个 plugin 解决的核心问题是：**在 Windows 平台上，通过 ADO/OLE DB 访问 SQL Server 数据库**。它是 DatabaseSupport plugin 的具体实现之一——DatabaseSupport 定义了抽象的数据库接口（`FDataBaseConnection`、`FDataBaseRecordSet`），而 ADOSupport 提供了基于 ADO 的 Windows 平台实现。

**重要限制**：此 plugin 仅支持 **Win64** 平台，且需要非 IWYU 编译模式。在其他平台或 IWYU 模式下，`USE_ADO_INTEGRATION` 被定义为 0，`CreateInstance()` 会返回一个空壳的 `FDataBaseConnection`（所有方法返回 false/0）。

## 使用场景

- 你的游戏需要在运行时查询 SQL Server 数据库（仅 Windows）
- 你正在开发内部工具，需要从数据库加载配置或统计数据
- 你有一个遗留系统使用 ADO 连接数据库，想在 UE 中复用相同的连接方式
- 你做的是企业级/模拟训练类应用，需要直接对接已有 SQL Server 数据库

**不适合的场景**：
- 跨平台项目（ADO 仅限 Windows）
- 高并发在线游戏（应使用 HTTP API 而非直接数据库连接）
- 使用 MySQL/PostgreSQL/SQLite 等非 SQL Server 数据库（ADO 理论上支持 OLE DB provider，但此 plugin 针对 SQL Server 优化）

## 蓝图用法

ADOSupport 没有暴露任何蓝图节点。它是一个纯 C++ Runtime 模块，不包含 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记。所有数据库操作必须通过 C++ 代码完成。

## C++ 用法

### 头文件引入

```cpp
#include "ADOSupport.h"
#include "Database.h"
```

### 模块启用

首先需要在项目的 `.uproject` 文件或 Editor 的 Plugins 面板中手动启用 ADOSupport（默认不启用）：

```json
{
    "Plugins": [
        {
            "Name": "ADOSupport",
            "Enabled": true
        }
    ]
}
```

### 基本用法

通过 `IADOSupport` 接口创建数据库连接实例，然后使用标准的 Open → Execute → Close 流程：

```cpp
#include "ADOSupport.h"
#include "Database.h"

// 检查模块是否可用
if (IADOSupport::IsAvailable())
{
    // 创建数据库连接实例
    IADOSupport& ADOSupport = IADOSupport::Get();
    FDataBaseConnection* Connection = ADOSupport.CreateInstance();

    // 打开连接（ADO 连接字符串格式）
    const TCHAR* ConnectionString = TEXT("Provider=SQLOLEDB;Data Source=MyServer;Initial Catalog=MyDB;Integrated Security=SSPI;");
    bool bConnected = Connection->Open(ConnectionString, TEXT(""), TEXT(""));

    if (bConnected)
    {
        // 执行不返回结果的 SQL 命令
        Connection->Execute(TEXT("INSERT INTO Players (Name, Score) VALUES ('Player1', 100)"));

        // 执行查询并获取结果集
        FDataBaseRecordSet* RecordSet = nullptr;
        Connection->Execute(TEXT("SELECT Name, Score FROM Players"), RecordSet);

        if (RecordSet)
        {
            // 遍历结果集
            for (FDataBaseRecordSet::TIterator It(RecordSet); It; ++It)
            {
                FString Name = It->GetString(TEXT("Name"));
                int32 Score = It->GetInt(TEXT("Score"));
                UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %d"), *Name, Score);
            }

            // 调用者负责删除 RecordSet
            delete RecordSet;
        }

        // 关闭连接
        Connection->Close();
    }

    delete Connection;
}
```

来源：基于 `ADOSupport.cpp`（`FADODataBaseConnection` 和 `FADODataBaseRecordSet` 的实现）和 `Database.h`（基类接口）。

### 进阶用法

#### 获取列信息

在不知道表结构时，可以用 `GetColumnNames()` 动态获取列名和类型：

```cpp
FDataBaseRecordSet* RecordSet = nullptr;
Connection->Execute(TEXT("SELECT * FROM Players"), RecordSet);

if (RecordSet)
{
    TArray<FDatabaseColumnInfo> Columns = RecordSet->GetColumnNames();
    for (const FDatabaseColumnInfo& ColInfo : Columns)
    {
        UE_LOG(LogTemp, Log, TEXT("Column: %s, Type: %d"), *ColInfo.ColumnName, (int32)ColInfo.DataType);
        // Type: DBT_INT=2, DBT_FLOAT=1, DBT_STRING=3
    }

    delete RecordSet;
}
```

#### 支持的数据类型读取

`FDataBaseRecordSet` 提供四种类型的读取方法：

| 方法 | 返回类型 | 对应 ADO 类型 |
|---|---|---|
| `GetString(Column)` | `FString` | adWChar, adVarWChar |
| `GetInt(Column)` | `int32` | adInteger |
| `GetFloat(Column)` | `float` | adSingle, adDouble |
| `GetBigInt(Column)` | `int64` | adBigInt |

## Demo 示例

### 最小可编译示例

**Build.cs 依赖配置：**

```csharp
using UnrealBuildTool;

public class MyDatabaseModule : ModuleRules
{
    public MyDatabaseModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "ADOSupport",    // 依赖 ADOSupport plugin
            "DatabaseSupport" // 依赖 DatabaseSupport plugin
        });
    }
}
```

**MyDBManager.h：**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Database.h"
#include "MyDBManager.generated.h"

UCLASS()
class AMyDBManager : public AActor
{
    GENERATED_BODY()

public:
    AMyDBManager();

    UFUNCTION(BlueprintCallable, Category = "Database")
    void QueryDatabase();

    UFUNCTION(BlueprintCallable, Category = "Database")
    void InsertPlayer(const FString& PlayerName, int32 Score);

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    FDataBaseConnection* DBConnection = nullptr;
};
```

**MyDBManager.cpp：**

```cpp
#include "MyDBManager.h"
#include "ADOSupport.h"

AMyDBManager::AMyDBManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDBManager::BeginPlay()
{
    Super::BeginPlay();

    if (IADOSupport::IsAvailable())
    {
        DBConnection = IADOSupport::Get().CreateInstance();
        const TCHAR* ConnStr = TEXT("Provider=SQLOLEDB;Data Source=.;Initial Catalog=GameDB;Integrated Security=SSPI;");
        if (!DBConnection->Open(ConnStr, TEXT(""), TEXT("")))
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open database connection"));
            delete DBConnection;
            DBConnection = nullptr;
        }
    }
}

void AMyDBManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (DBConnection)
    {
        DBConnection->Close();
        delete DBConnection;
        DBConnection = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void AMyDBManager::QueryDatabase()
{
    if (!DBConnection) return;

    FDataBaseRecordSet* RecordSet = nullptr;
    if (DBConnection->Execute(TEXT("SELECT Name, Score FROM Players ORDER BY Score DESC"), RecordSet) && RecordSet)
    {
        for (FDataBaseRecordSet::TIterator It(RecordSet); It; ++It)
        {
            UE_LOG(LogTemp, Log, TEXT("%s: %d"), *It->GetString(TEXT("Name")), It->GetInt(TEXT("Score")));
        }
        delete RecordSet;
    }
}

void AMyDBManager::InsertPlayer(const FString& PlayerName, int32 Score)
{
    if (!DBConnection) return;

    FString Query = FString::Printf(TEXT("INSERT INTO Players (Name, Score) VALUES ('%s', %d)"), *PlayerName, Score);
    DBConnection->Execute(*Query);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `DatabaseSupport` | 提供 `FDataBaseConnection`、`FDataBaseRecordSet` 抽象基类和 `FDatabaseColumnInfo` 结构体 |

### 外部依赖

- **msado15.dll**：Windows 系统自带的 ADO 类型库，位于 `Common Files\System\ADO\` 目录
- **COM 运行时**：通过 `FWindowsPlatformMisc::CoInitialize()` 初始化

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-18 | `c61e4278e7d8` | Various fixes to make unreal editor compile with IWYU | IWYU 兼容性修复，确保在 IWYU 模式下能正常编译（ADO 集成会被禁用） |
| 2025-03-27 | `4b8ede3f2a89` | ADOSupport: Don't throw an exception if exceptions aren't enabled | 修复在禁用异常的平台上 `_com_error` 编译失败的问题 |
| 2025-02-19 | `2c7c1f6882e9` | GenerateTLH clang fixes | 修复 ADO 类型库头文件生成的 clang 编译兼容性问题 |

### 维护评价

- **年龄**：7 年多（2019 年 1 月创建）
- **维护频率**：低频维护，2025 年有 3 次编译兼容性修复，但没有功能性更新
- **状态**：处于维护模式——只做编译修复，不添加新功能
- **已知限制**：仅 Win64 平台，非 IWYU 编译模式下才有实际功能
- **是否推荐使用**：仅推荐在明确需要 ADO/SQL Server 的 Windows 专用项目中使用。对于新项目，建议考虑更现代的数据库连接方案（如直接使用第三方库或 HTTP API）

这是一个非常古老的模块（代码风格保留了大量 UE3 时代的痕迹），核心功能已经很久没有变化。近期的 commit 都是编译层面的修复，说明 Epic 仍在确保它能编译通过，但没有投入精力发展它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/ADOSupport)
- [DatabaseSupport（父插件）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/DatabaseSupport)
- 官方文档：无
