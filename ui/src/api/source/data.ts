import {PageResult} from "@/api/PageResult";

export interface SourceResultPage extends PageResult {
    items: SourceResult[];
}

export interface SourceResult {
    id: any
    title: string
    type: string
    status: string
    configuration: any
    progress: any
    document_count: number
}

export interface SourceCreatePayload {
    title: string
    type: string
    description: string
    url: string
    is_cloud: boolean
    username: string
    password: string
    space_key: string
    search_query: string
}

export interface SourceConfiguration {}

export class AtlassianConfiguration implements SourceConfiguration {
    url: string
    is_cloud: boolean
    username: string
    password: string

    constructor(form: SourceCreatePayload) {
        this.url = form.url;
        this.is_cloud = form.is_cloud;
        this.username = form.username;
        this.password = form.password;
    }
}

export class ConfluenceConfiguration extends AtlassianConfiguration {
    space_key: string

    constructor(form: SourceCreatePayload) {
        super(form);
        this.space_key = form.space_key;
    }
}

export class JiraConfiguration extends AtlassianConfiguration {
    search_query: string

    constructor(form: SourceCreatePayload) {
        super(form);
        this.search_query = form.search_query;
    }
}
