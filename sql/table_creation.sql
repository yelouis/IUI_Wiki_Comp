--
-- PostgreSQL database dump
--

-- Dumped from database version 14.0
-- Dumped by pg_dump version 14.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: article; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.article (
    id integer NOT NULL,
    title character varying,
    currentid integer,
    num_edits integer,
    num_unique_authors integer,
    author_diversity real,
    age integer,
    currency integer,
    author_density bigint,
    author_score real,
    article_quality integer,
    full_author_density bigint,
    quotescore double precision,
    nonquotescore double precision,
    model_score real
);


ALTER TABLE public.article OWNER TO wikipedia;

--
-- Name: article_author_scores; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.article_author_scores (
    article_id integer,
    sum numeric
);


ALTER TABLE public.article_author_scores OWNER TO wikipedia;

--
-- Name: article_quality; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.article_quality (
    name character varying NOT NULL,
    score integer
);


ALTER TABLE public.article_quality OWNER TO wikipedia;

--
-- Name: author_scores; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.author_scores (
    real_id character varying,
    sum bigint
);


ALTER TABLE public.author_scores OWNER TO wikipedia;

--
-- Name: author_sum; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.author_sum (
    article_id integer,
    count numeric
);


ALTER TABLE public.author_sum OWNER TO wikipedia;

--
-- Name: complete_article_quality; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.complete_article_quality (
    title character varying,
    score integer
);


ALTER TABLE public.complete_article_quality OWNER TO wikipedia;

--
-- Name: complete_author_sum; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.complete_author_sum (
    article_id integer,
    count numeric
);


ALTER TABLE public.complete_author_sum OWNER TO wikipedia;

--
-- Name: connectivity_graph; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.connectivity_graph (
    autha character varying,
    authb character varying,
    count bigint
);


ALTER TABLE public.connectivity_graph OWNER TO wikipedia;

--
-- Name: filtered_graph; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.filtered_graph (
    autha character varying,
    authb character varying,
    count bigint
);


ALTER TABLE public.filtered_graph OWNER TO wikipedia;

--
-- Name: mtie; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public.mtie (
    x integer
);


ALTER TABLE public.mtie OWNER TO wikipedia;

--
-- Name: revisionHistory; Type: TABLE; Schema: public; Owner: wikipedia
--

CREATE TABLE public."revisionHistory" (
    revision_id integer NOT NULL,
    title character varying,
    num_internal_links integer,
    num_external_links integer,
    article_length integer,
    article_id integer,
    flesch real,
    kincaid real,
    num_images integer,
    average_sentence_length real,
    date date,
    text text,
    a_name character varying,
    a_id integer,
    a_ip character varying,
    real_id character varying
);


ALTER TABLE public."revisionHistory" OWNER TO wikipedia;

--
-- Name: revisionHistory_id_seq; Type: SEQUENCE; Schema: public; Owner: wikipedia
--

CREATE SEQUENCE public."revisionHistory_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."revisionHistory_id_seq" OWNER TO wikipedia;

--
-- Name: revisionHistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wikipedia
--

ALTER SEQUENCE public."revisionHistory_id_seq" OWNED BY public."revisionHistory".revision_id;


--
-- Name: sectionMetrics; Type: TABLE; Schema: public; Owner: mathcsadmin
--

CREATE TABLE public."sectionMetrics" (
    id integer NOT NULL,
    "articleName" character varying,
    "sectionName" character varying,
    "isSummary" boolean,
    num_int_links integer,
    num_ext_links integer,
    "revisionId" integer
);


ALTER TABLE public."sectionMetrics" OWNER TO mathcsadmin;

--
-- Name: sectionMetrics_id_seq; Type: SEQUENCE; Schema: public; Owner: mathcsadmin
--

CREATE SEQUENCE public."sectionMetrics_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."sectionMetrics_id_seq" OWNER TO mathcsadmin;

--
-- Name: sectionMetrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mathcsadmin
--

ALTER SEQUENCE public."sectionMetrics_id_seq" OWNED BY public."sectionMetrics".id;


--
-- Name: revisionHistory revision_id; Type: DEFAULT; Schema: public; Owner: wikipedia
--

ALTER TABLE ONLY public."revisionHistory" ALTER COLUMN revision_id SET DEFAULT nextval('public."revisionHistory_id_seq"'::regclass);


--
-- Name: sectionMetrics id; Type: DEFAULT; Schema: public; Owner: mathcsadmin
--

ALTER TABLE ONLY public."sectionMetrics" ALTER COLUMN id SET DEFAULT nextval('public."sectionMetrics_id_seq"'::regclass);


--
-- Name: article article_pkey; Type: CONSTRAINT; Schema: public; Owner: wikipedia
--

ALTER TABLE ONLY public.article
    ADD CONSTRAINT article_pkey PRIMARY KEY (id);


--
-- Name: article_quality article_quality_pkey; Type: CONSTRAINT; Schema: public; Owner: wikipedia
--

ALTER TABLE ONLY public.article_quality
    ADD CONSTRAINT article_quality_pkey PRIMARY KEY (name);


--
-- Name: revisionHistory revisionHistory_pkey; Type: CONSTRAINT; Schema: public; Owner: wikipedia
--

ALTER TABLE ONLY public."revisionHistory"
    ADD CONSTRAINT "revisionHistory_pkey" PRIMARY KEY (revision_id);


--
-- Name: sectionMetrics sectionMetrics_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcsadmin
--

ALTER TABLE ONLY public."sectionMetrics"
    ADD CONSTRAINT "sectionMetrics_pkey" PRIMARY KEY (id);


--
-- Name: article_id_index; Type: INDEX; Schema: public; Owner: wikipedia
--

CREATE INDEX article_id_index ON public."revisionHistory" USING btree (article_id);


--
-- Name: real_id_index; Type: INDEX; Schema: public; Owner: wikipedia
--

CREATE INDEX real_id_index ON public."revisionHistory" USING btree (real_id);


--
-- Name: revisionHistory revisionHistory_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wikipedia
--

ALTER TABLE ONLY public."revisionHistory"
    ADD CONSTRAINT "revisionHistory_article_id_fkey" FOREIGN KEY (article_id) REFERENCES public.article(id);


--
-- Name: sectionMetrics sectionMetrics_revisionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mathcsadmin
--

ALTER TABLE ONLY public."sectionMetrics"
    ADD CONSTRAINT "sectionMetrics_revisionId_fkey" FOREIGN KEY ("revisionId") REFERENCES public."revisionHistory"(revision_id);


--
-- PostgreSQL database dump complete
--

