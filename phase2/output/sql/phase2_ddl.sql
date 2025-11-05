--
-- PostgreSQL database dump
--

\restrict 9H6HoQhTgtjeDvubvoDyfBCira8x4fw88PhZfhEPuDfmKeSgGLQ0ZwQUPEMjfS0

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0 (Debian 18.0-1.pgdg13+3)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: customer_reservations; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.customer_reservations (
    id text,
    hotel text,
    lead_time integer,
    arrival_year integer,
    arrival_month integer,
    arrival_date_week_number integer,
    arrival_date_day_of_month integer,
    stays_in_weekend_nights integer,
    stays_in_week_nights integer,
    market_segment_type text,
    country text,
    avg_price_per_room double precision,
    email text,
    is_canceled boolean NOT NULL
);


ALTER TABLE public.customer_reservations OWNER TO admin;

--
-- Name: hotel_bookings; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.hotel_bookings (
    id text,
    hotel text,
    lead_time integer,
    arrival_year integer,
    arrival_month integer,
    arrival_date_week_number integer,
    arrival_date_day_of_month integer,
    stays_in_weekend_nights integer,
    stays_in_week_nights integer,
    market_segment_type text,
    country text,
    avg_price_per_room double precision,
    email text,
    is_canceled boolean NOT NULL
);


ALTER TABLE public.hotel_bookings OWNER TO admin;

--
-- Name: merged_hotel_data; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.merged_hotel_data (
    id text,
    hotel text,
    lead_time integer,
    arrival_year integer,
    arrival_month integer,
    arrival_date_week_number integer,
    arrival_date_day_of_month integer,
    stays_in_weekend_nights integer,
    stays_in_week_nights integer,
    market_segment_type text,
    country text,
    avg_price_per_room double precision,
    email text,
    is_canceled boolean
);


ALTER TABLE public.merged_hotel_data OWNER TO admin;

--
-- Name: customer_reservations_idx_date; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX customer_reservations_idx_date ON public.customer_reservations USING btree (arrival_year, arrival_month);


--
-- Name: customer_reservations_idx_price; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX customer_reservations_idx_price ON public.customer_reservations USING btree (avg_price_per_room);


--
-- Name: customer_reservations_idx_segment; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX customer_reservations_idx_segment ON public.customer_reservations USING btree (market_segment_type);


--
-- Name: customer_reservations_idx_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX customer_reservations_idx_status ON public.customer_reservations USING btree (is_canceled);


--
-- Name: hotel_bookings_idx_date; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX hotel_bookings_idx_date ON public.hotel_bookings USING btree (arrival_year, arrival_month);


--
-- Name: hotel_bookings_idx_price; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX hotel_bookings_idx_price ON public.hotel_bookings USING btree (avg_price_per_room);


--
-- Name: hotel_bookings_idx_segment; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX hotel_bookings_idx_segment ON public.hotel_bookings USING btree (market_segment_type);


--
-- Name: hotel_bookings_idx_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX hotel_bookings_idx_status ON public.hotel_bookings USING btree (is_canceled);


--
-- Name: merged_hotel_data_idx_date; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX merged_hotel_data_idx_date ON public.merged_hotel_data USING btree (arrival_year, arrival_month);


--
-- Name: merged_hotel_data_idx_price; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX merged_hotel_data_idx_price ON public.merged_hotel_data USING btree (avg_price_per_room);


--
-- Name: merged_hotel_data_idx_segment; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX merged_hotel_data_idx_segment ON public.merged_hotel_data USING btree (market_segment_type);


--
-- Name: merged_hotel_data_idx_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX merged_hotel_data_idx_status ON public.merged_hotel_data USING btree (is_canceled);


--
-- PostgreSQL database dump complete
--

\unrestrict 9H6HoQhTgtjeDvubvoDyfBCira8x4fw88PhZfhEPuDfmKeSgGLQ0ZwQUPEMjfS0

