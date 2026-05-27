# SQLite Support

> SQLite Database Support（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | SQLite数据库支持 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SQLiteSupport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteSupport) | |

## 用途

为 Unreal Engine 提供 SQLite 数据库的运行时访问能力。该插件基于 UE 的通用数据库抽象层（`DatabaseSupport`），实现了 SQLite 特有的连接管理和结果集处理。它封装了 `SQLiteCore` 底层库，让开发者可以用统一的 `FDataBaseConnection`/`FDataBaseRecordSet` 接口来执行 SQL 查询、读取结果，而无需直接与 SQLite C API 交互。

## 使用场景

- 你有一个本地存档系统，需要结构化存储玩家进度、配置数据 → 用 SQLite 替代纯 JSON 文件
- 你正在开发离线单机游戏，需要一个轻量级的本地数据库来管理游戏数据表 → 用 SQLiteSupport
- 你需要在运行时执行复杂的 SQL 查询（JOIN、聚合、索引）而非简单的键值查找 → 用 SQLiteSupport
- 你需要将外部导入的 `.db` 文件作为游戏资源使用 → 用 SQLiteSupport

## 蓝图用法

该插件没有暴露任何蓝图节点。所有 API 均为 C++ 接口，适合在 C++ 代码中直接使用。

## C++ 用法

### 头文件引入

```cpp
#include "SQLiteSupport.h"
#include "SQLiteDatabaseConnection.h"
#include "SQLiteResultSet.h"
```

### 基本用法

以下示例展示如何打开数据库、执行查询并读取结果：

```cpp
// 创建数据库连接
FSQLiteDatabaseConnection Connection;

// 打开本地 SQLite 数据库文件
const FString DbPath = FPaths::ProjectSavedDir() / TEXT("MyGame.db");
if (Connection.Open(*DbPath, nullptr, nullptr))
{
    UE_LOG(LogTemp, Log, TEXT("数据库打开成功"));
}

// 执行无返回结果的命令（建表、插入等）
bool bSuccess = Connection.Execute(TEXT(
    "CREATE TABLE IF NOT EXISTS Players ("
    "  Id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  Name TEXT NOT NULL,"
    "  Score REAL DEFAULT 0"
    ")"
));

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("建表成功"));
}

// 插入数据
Connection.Execute(TEXT("INSERT INTO Players (Name, Score) VALUES ('Alice', 95.5)"));

// 关闭连接
Connection.Close();
```

### 进阶用法

执行带返回结果集的查询，遍历读取字段数据：

```cpp
#include "SQLiteDatabaseConnection.h"
#include "SQLiteResultSet.h"

FSQLiteDatabaseConnection Connection;
if (Connection.Open(TEXT("/path/to/database.db"), nullptr, nullptr))
{
    FSQLiteResultSet* ResultSet = nullptr;

    // 执行查询并获取结果集
    if (Connection.Execute(TEXT("SELECT Id, Name, Score FROM Players ORDER BY Score DESC"), ResultSet)
        && ResultSet != nullptr)
    {
        // 遍历所有记录
        for (ResultSet->MoveToFirst(); !ResultSet->IsAtEnd(); ResultSet->MoveToNext())
        {
            const int32 Id = ResultSet->GetInt(TEXT("Id"));
            const FString Name = ResultSet->GetString(TEXT("Name"));
            const float Score = ResultSet->GetFloat(TEXT("Score"));

            UE_LOG(LogTemp, Log, TEXT("Player %d: %s, Score: %.1f"), Id, *Name, Score);
        }

        // 获取记录总数
        int32 RecordCount = ResultSet->GetRecordCount();
        UE_LOG(LogTemp, Log, TEXT("共 %d 条记录"), RecordCount);

        // 获取列信息
        TArray<FDatabaseColumnInfo> Columns = ResultSet->GetColumnNames();
        for (const auto& Column : Columns)
        {
            UE_LOG(LogTemp, Log, TEXT("列名: %s"), *Column.ColumnName);
        }

        // 检查错误
        if (ResultSet->HasError())
        {
            UE_LOG(LogTemp, Error, TEXT("查询错误 [%d]: %s"),
                ResultSet->GetErrorCode(), *ResultSet->GetErrorMessage());
        }

        // 调用者负责释放结果集
        delete ResultSet;
        ResultSet = nullptr;
    }

    Connection.Close();
}

// 检查模块是否可用
if (ISQLiteSupport::IsAvailable())
{
    ISQLiteSupport& Support = ISQLiteSupport::Get();
    // 模块已加载，可使用
}

// 获取最近的错误信息
FString LastError = Connection.GetLastError();
if (!LastError.IsEmpty())
{
    UE_LOG(LogTemp, Error, TEXT("数据库错误: %s"), *LastError);
}
```

## Demo 示例

一个最小完整的使用示例，展示连接、建表、插入、查询的全流程：

**SQLiteDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FSQLiteDemo
{
public:
    /** 初始化数据库并执行完整的 CRUD 演示 */
    static void RunDemo();
};
```

**SQLiteDemo.cpp**
```cpp
#include "SQLiteDemo.h"
#include "SQLiteSupport.h"
#include "SQLiteDatabaseConnection.h"
#include "SQLiteResultSet.h"

void FSQLiteDemo::RunDemo()
{
    // 确保模块可用
    if (!ISQLiteSupport::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("SQLiteSupport 模块未加载"));
        return;
    }

    FSQLiteDatabaseConnection DB;
    const FString DbPath = FPaths::ProjectSavedDir() / TEXT("demo.db");

    // 打开数据库
    if (!DB.Open(*DbPath, nullptr, nullptr))
    {
        UE_LOG(LogTemp, Error, TEXT("无法打开数据库: %s"), *DB.GetLastError());
        return;
    }

    // 建表
    DB.Execute(TEXT(
        "CREATE TABLE IF NOT EXISTS Items ("
        "  Id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  Name TEXT NOT NULL,"
        "  Quantity INTEGER DEFAULT 0"
        ")"
    ));

    // 清空旧数据
    DB.Execute(TEXT("DELETE FROM Items"));

    // 插入数据
    DB.Execute(TEXT("INSERT INTO Items (Name, Quantity) VALUES ('Sword', 1)"));
    DB.Execute(TEXT("INSERT INTO Items (Name, Quantity) VALUES ('Shield', 2)"));
    DB.Execute(TEXT("INSERT INTO Items (Name, Quantity) VALUES ('Potion', 10)"));

    // 查询数据
    FSQLiteResultSet* ResultSet = nullptr;
    if (DB.Execute(TEXT("SELECT Name, Quantity FROM Items WHERE Quantity > 1"), ResultSet)
        && ResultSet)
    {
        UE_LOG(LogTemp, Log, TEXT("数量大于1的物品:"));
        for (ResultSet->MoveToFirst(); !ResultSet->IsAtEnd(); ResultSet->MoveToNext())
        {
            UE_LOG(LogTemp, Log, TEXT("  %s x%d"),
                *ResultSet->GetString(TEXT("Name")),
                ResultSet->GetInt(TEXT("Quantity")));
        }
        delete ResultSet;
    }

    // 关闭数据库
    DB.Close();
}
```

## 模块依赖

该插件依赖以下插件（在 .uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `DatabaseSupport` | UE 通用数据库抽象层，提供 `FDataBaseConnection`/`FDataBaseRecordSet` 基类 |
| `SQLiteCore` | SQLite 底层 C 库封装，提供 `FSQLiteDatabase`、`FSQLitePreparedStatement` 等核心类型 |

你的模块 Build.cs 通常只需依赖 `SQLiteSupport` 即可，运行时会自动拉入上述依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 新日志宏 |
| 2025-10-31 | `c57f0b00` | Clarified that the output param of Step was only filled for error cases, and not when a row is returned. | 明确 Step 输出参数仅在错误时填充 |
| 2025-10-31 | `c8c0f285` | PR #12093: add error detection for SQLiteSupport | 为 SQLiteSupport 增加错误检测功能 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量维护性更新 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的第三方链接更新为安全协议 |

### 维护评价

该插件于 2019 年创建，已有约 6 年历史，属于老古董级别。从最近的 commit 来看，2025 年底有实质性的错误检测功能增强（PR #12093），2026 年初有日志宏迁移的工程性更新，表明仍在持续维护中。

该插件规模很小（仅约 6 个源文件），功能单一且稳定，基本不会出现重大 bug。**默认未启用**（`EnabledByDefault: false`），需要在项目设置中手动开启。

作为 Epic 官方维护的插件，代码质量可靠，适合作为本地数据库方案使用。唯一需要注意的是它不提供蓝图接口，纯 C++ 使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteSupport)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteSupport/Tests)（如存在）